"""NEURO-BEAM leakage-safe transcriptome -> electrophysiology predictive benchmark.

Primary purpose: quantify whether transcriptomic information predicts measured
electrical traits under subject-grouped cross-validation, and whether CBEF
prioritized genes retain predictive information.

This is a benchmark layer; it does not infer causality.
"""
from __future__ import annotations
import json,re
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.cross_decomposition import PLSRegression
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import r2_score, mean_absolute_error

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
BASE="https://raw.githubusercontent.com/daifengwanglab/scMNC/main/mouse_visual_cortex/data/"
E_URL=BASE+"efeature.csv"
G_URL=BASE+"geneExp_filtered.csv"
M_URL=BASE+"20200711_patchseq_metadata_mouse.csv"

TRAITS=[
 "vrest","ri","sag","tau","f_i_curve_slope","adaptation","latency","avg_isi",
 "upstroke_downstroke_ratio_long_square","peak_v_long_square","trough_v_long_square",
 "fast_trough_v_long_square","threshold_v_long_square","threshold_i_long_square",
 "threshold_v_short_square","threshold_i_short_square","threshold_v_ramp","threshold_i_ramp"
]

def session(v):
    t=re.findall(r"\d+",str(v));return t[1] if len(t)>=2 else None
def subject(v):
    t=re.findall(r"\d+",str(v));return t[0] if len(t)>=1 else None

def load():
    e=pd.read_csv(E_URL);g=pd.read_csv(G_URL);m=pd.read_csv(M_URL)
    e["_session"]=e["ID"].map(session).astype(str);e["_subject"]=e["ID"].map(subject).astype(str)
    mm=m[["ephys_session_id","transcriptomics_sample_id"]].copy()
    mm["_session"]=mm["ephys_session_id"].astype(str).str.replace(r"\.0$","",regex=True)
    e["_session"]=e["_session"].str.replace(r"\.0$","",regex=True)
    e=e.merge(mm[["_session","transcriptomics_sample_id"]],on="_session",how="left")
    g=g.drop_duplicates("gene").set_index("gene")
    e=e[e["transcriptomics_sample_id"].astype(str).isin(g.columns)].drop_duplicates("transcriptomics_sample_id")
    e=e.set_index(e["transcriptomics_sample_id"].astype(str))
    cells=[c for c in e.index if c in g.columns]
    e=e.loc[cells]; g=g[cells]
    X=g.T.apply(pd.to_numeric,errors="coerce")
    # Rank-preserving log transform only when values are non-negative.
    if np.nanmin(X.to_numpy(float))>=0: X=np.log1p(X)
    X=X.fillna(X.median())
    ys=[t for t in TRAITS if t in e.columns]
    Y=e[ys].apply(pd.to_numeric,errors="coerce")
    valid=Y.notna().all(axis=1)
    X=X.loc[valid];Y=Y.loc[valid];groups=e.loc[valid,"_subject"].astype(str)
    return X,Y,groups

def metrics(y,p):
    out=[]
    for j,c in enumerate(y.columns):
        yt=y.iloc[:,j].to_numpy(float);yp=p[:,j]
        rho=spearmanr(yt,yp,nan_policy="omit").statistic
        out.append({"trait":c,"r2":float(r2_score(yt,yp)),
                    "mae":float(mean_absolute_error(yt,yp)),
                    "spearman":float(rho) if np.isfinite(rho) else None})
    return out

def main():
    X,Y,groups=load()
    # deterministic variance subset for tree model
    var=X.var(axis=0).sort_values(ascending=False)
    tree_genes=var.head(min(400,len(var))).index.tolist()

    top500=None
    p=DATA/"top500_gene_catalog.csv"
    if p.exists():
        cat=pd.read_csv(p)
        mouse=[x for x in cat.get("mouse_gene",pd.Series(dtype=str)).astype(str) if x in X.columns]
        if len(mouse)>=50: top500=mouse[:500]

    gkf=GroupKFold(n_splits=5)
    rows=[];predictions=[]
    for fold,(tr,te) in enumerate(gkf.split(X,Y,groups),1):
        Xtr,Xte=X.iloc[tr],X.iloc[te];Ytr,Yte=Y.iloc[tr],Y.iloc[te]

        models={
          "ridge_all":Pipeline([("z",StandardScaler()),("m",Ridge(alpha=100.0))]),
          "pls_all":Pipeline([("z",StandardScaler()),("m",PLSRegression(n_components=min(20,len(Y.columns)+2),scale=False,max_iter=500))]),
          "extra_trees_var400":ExtraTreesRegressor(n_estimators=180,min_samples_leaf=4,max_features=.45,n_jobs=-1,random_state=42+fold)
        }
        views={
          "ridge_all":list(X.columns),
          "pls_all":list(X.columns),
          "extra_trees_var400":tree_genes
        }
        if top500:
            models["ridge_cbe_top500"]=Pipeline([("z",StandardScaler()),("m",Ridge(alpha=100.0))])
            views["ridge_cbe_top500"]=top500

        for name,model in models.items():
            cols=views[name]
            model.fit(Xtr[cols],Ytr)
            pred=np.asarray(model.predict(Xte[cols]))
            if pred.ndim==1: pred=pred[:,None]
            for x in metrics(Yte,pred):
                x.update({"fold":fold,"model":name,"n_train":len(tr),"n_test":len(te),
                          "n_genes":len(cols),"n_groups_train":groups.iloc[tr].nunique(),
                          "n_groups_test":groups.iloc[te].nunique()})
                rows.append(x)

    res=pd.DataFrame(rows)
    res.to_csv(DATA/"predictive_benchmark_folds.csv",index=False)
    summary=res.groupby(["model","trait"]).agg(
        mean_r2=("r2","mean"),sd_r2=("r2","std"),
        mean_mae=("mae","mean"),mean_spearman=("spearman","mean"),
        folds=("fold","count"),n_genes=("n_genes","first")
    ).reset_index()
    summary.to_csv(DATA/"predictive_benchmark_summary.csv",index=False)

    overall=summary.groupby("model").agg(
        mean_trait_r2=("mean_r2","mean"),
        median_trait_r2=("mean_r2","median"),
        mean_trait_spearman=("mean_spearman","mean"),
        mean_trait_mae=("mean_mae","mean"),
        traits=("trait","count"),n_genes=("n_genes","first")
    ).reset_index().sort_values("mean_trait_r2",ascending=False)
    payload={"nCells":len(X),"nGenes":X.shape[1],"nSubjects":groups.nunique(),
             "traits":list(Y.columns),"models":overall.to_dict(orient="records"),
             "perTrait":summary.to_dict(orient="records"),
             "split":"5-fold GroupKFold using subject ID parsed from electrophysiology NWB identifiers",
             "guardrail":"All preprocessing is fitted inside each model pipeline; subject groups do not cross train/test folds."}
    (DATA/"predictive_benchmark.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    print(json.dumps(payload["models"],indent=2))

if __name__=="__main__": main()
