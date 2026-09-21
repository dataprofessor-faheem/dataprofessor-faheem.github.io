"""Leakage-safe transcriptome -> electrophysiology benchmark for NEURO-BEAM.

Visual-cortex Patch-seq:
- explicit same-cell alignment via ephys_session_id -> transcriptomics_sample_id
- subject/group ID reconstructed from NWB ID
- per-cell expression percentile-rank normalization for platform robustness
- GroupKFold by subject
- Ridge and ExtraTrees baselines
- fold-local variance feature selection for ExtraTrees
"""
from __future__ import annotations
import json,re
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import r2_score, mean_absolute_error

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data";DATA.mkdir(parents=True,exist_ok=True)
BASE="https://raw.githubusercontent.com/daifengwanglab/scMNC/main/mouse_visual_cortex/data/"
E_URL=BASE+"efeature.csv";G_URL=BASE+"geneExp_filtered.csv";M_URL=BASE+"20200711_patchseq_metadata_mouse.csv"

TARGETS=[
  "vrest","ri","tau","f_i_curve_slope","adaptation","latency",
  "avg_isi","upstroke_downstroke_ratio_long_square",
  "threshold_v_long_square","threshold_i_long_square","sag"
]

def toks(v):return re.findall(r"\d+",str(v))

def load():
    e=pd.read_csv(E_URL);g=pd.read_csv(G_URL);m=pd.read_csv(M_URL)
    e=e.copy()
    e["_subject_id"]=e["ID"].map(lambda x:toks(x)[0] if len(toks(x))>=2 else None)
    e["_session_id"]=e["ID"].map(lambda x:toks(x)[1] if len(toks(x))>=2 else None)
    mm=m[["ephys_session_id","transcriptomics_sample_id","t_type"]].copy()
    mm["_session_id"]=mm.ephys_session_id.astype(str).str.replace(r"\.0$","",regex=True)
    e["_session_id"]=e["_session_id"].astype(str).str.replace(r"\.0$","",regex=True)
    e=e.merge(mm,on="_session_id",how="left")
    gene_col="gene" if "gene" in g.columns else g.columns[0]
    g=g.drop_duplicates(subset=[gene_col]).set_index(gene_col)
    e=e[e.transcriptomics_sample_id.astype(str).isin(g.columns)].drop_duplicates("transcriptomics_sample_id")
    e=e.set_index(e.transcriptomics_sample_id.astype(str))
    shared=[x for x in e.index if x in g.columns]
    e=e.loc[shared];g=g[shared]
    targets=[x for x in TARGETS if x in e.columns]
    Y=e[targets].apply(pd.to_numeric,errors="coerce")
    keep=Y.notna().all(axis=1)
    e=e.loc[keep];Y=Y.loc[keep];g=g[e.index]
    # within-cell rank-normalization yields [0,1] and is robust to expression scale.
    X=g.apply(pd.to_numeric,errors="coerce").fillna(0).rank(axis=0,pct=True).T
    groups=e["_subject_id"].astype(str).values
    return X,Y,groups,e

def metrics(y,p,target,model,fold):
    ok=np.isfinite(y)&np.isfinite(p)
    if ok.sum()<10:return None
    rho,_=spearmanr(y[ok],p[ok])
    return {
      "model":model,"fold":fold,"target":target,"n":int(ok.sum()),
      "r2":float(r2_score(y[ok],p[ok])),
      "mae":float(mean_absolute_error(y[ok],p[ok])),
      "spearman":float(rho)
    }

def main():
    X,Y,groups,e=load()
    gkf=GroupKFold(n_splits=5)
    rows=[];pred_rows=[]
    Xv=X.to_numpy(float);Yv=Y.to_numpy(float)
    genes=np.array(X.columns)
    targets=list(Y.columns)

    for fold,(tr,te) in enumerate(gkf.split(Xv,Yv,groups),1):
        # Ridge: standardize X and Y on training fold only.
        xs=StandardScaler().fit(Xv[tr]); ys=StandardScaler().fit(Yv[tr])
        xtr=xs.transform(Xv[tr]);xte=xs.transform(Xv[te])
        ytr=ys.transform(Yv[tr])
        ridge=Ridge(alpha=100.0).fit(xtr,ytr)
        pr=ys.inverse_transform(ridge.predict(xte))

        # ExtraTrees: select top 300 variable genes using training fold only.
        var=np.nanvar(Xv[tr],axis=0)
        sel=np.argsort(var)[-min(300,len(var)):]
        et=ExtraTreesRegressor(
            n_estimators=220,max_features="sqrt",min_samples_leaf=4,
            n_jobs=-1,random_state=1000+fold
        ).fit(Xv[tr][:,sel],Yv[tr])
        pe=et.predict(Xv[te][:,sel])

        for j,t in enumerate(targets):
            for model,pred in [("Ridge",pr[:,j]),("ExtraTrees",pe[:,j])]:
                r=metrics(Yv[te,j],pred,t,model,fold)
                if r:rows.append(r)
            for idx,k in enumerate(te):
                pred_rows.append({
                    "cell_id":X.index[k],"subject_id":groups[k],"fold":fold,"target":t,
                    "observed":Yv[k,j],"ridge_pred":pr[idx,j],"extratrees_pred":pe[idx,j]
                })

    res=pd.DataFrame(rows)
    res.to_csv(DATA/"ml_grouped_cv_metrics_by_fold.csv",index=False)
    pd.DataFrame(pred_rows).to_csv(DATA/"ml_grouped_cv_predictions.csv",index=False)
    summary=res.groupby(["model","target"]).agg(
        r2_mean=("r2","mean"),r2_sd=("r2","std"),
        spearman_mean=("spearman","mean"),spearman_sd=("spearman","std"),
        mae_mean=("mae","mean"),mae_sd=("mae","std")
    ).reset_index()
    summary.to_csv(DATA/"ml_grouped_cv_summary.csv",index=False)

    # Fit final ExtraTrees on all cells to export stable global importances for discovery only.
    var=np.nanvar(Xv,axis=0);sel=np.argsort(var)[-min(300,len(var)):]
    final=ExtraTreesRegressor(n_estimators=350,max_features="sqrt",min_samples_leaf=4,n_jobs=-1,random_state=42).fit(Xv[:,sel],Yv)
    imp=pd.DataFrame({"gene":genes[sel],"importance":final.feature_importances_}).sort_values("importance",ascending=False)
    imp.to_csv(DATA/"ml_extratrees_global_feature_importance.csv",index=False)

    payload={
      "nCells":int(len(X)),"nSubjects":int(len(set(groups))),"nGenes":int(X.shape[1]),
      "targets":targets,"split":"5-fold GroupKFold by subject ID",
      "normalization":"within-cell gene percentile rank",
      "models":["Ridge(alpha=100)","ExtraTrees(220 trees; fold-local top-300 variance genes)"],
      "summary":summary.replace({np.nan:None}).to_dict(orient="records"),
      "interpretation":"Internal grouped-CV benchmark only; external M1 remains required for generalization claims."
    }
    (DATA/"ml_grouped_cv_summary.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    print(json.dumps({"nCells":payload["nCells"],"nSubjects":payload["nSubjects"],"nGenes":payload["nGenes"],"best":summary.sort_values("spearman_mean",ascending=False).head(12).to_dict(orient="records")},indent=2))

if __name__=="__main__":main()
