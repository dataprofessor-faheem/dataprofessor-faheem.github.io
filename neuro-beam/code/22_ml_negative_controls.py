"""Leakage, permutation and baseline-control experiments for NEURO-BEAM."""
from __future__ import annotations
import json,re
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.model_selection import GroupKFold,KFold
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import r2_score

ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/"data"
BASE="https://raw.githubusercontent.com/daifengwanglab/scMNC/main/mouse_visual_cortex/data/"
E_URL=BASE+"efeature.csv";G_URL=BASE+"geneExp_filtered.csv";M_URL=BASE+"20200711_patchseq_metadata_mouse.csv"
TARGETS=["vrest","ri","tau","f_i_curve_slope","adaptation","latency","avg_isi","upstroke_downstroke_ratio_long_square","threshold_v_long_square","threshold_i_long_square","sag"]

def toks(v):return re.findall(r"\d+",str(v))
def load():
    e=pd.read_csv(E_URL);g=pd.read_csv(G_URL);m=pd.read_csv(M_URL)
    e["_subject"]=e.ID.map(lambda x:toks(x)[0] if len(toks(x))>=2 else None)
    e["_session"]=e.ID.map(lambda x:toks(x)[1] if len(toks(x))>=2 else None)
    mm=m[["ephys_session_id","transcriptomics_sample_id"]].copy();mm["_session"]=mm.ephys_session_id.astype(str).str.replace(r"\.0$","",regex=True)
    e["_session"]=e["_session"].astype(str).str.replace(r"\.0$","",regex=True)
    e=e.merge(mm[["_session","transcriptomics_sample_id"]],on="_session",how="left")
    g=g.drop_duplicates("gene").set_index("gene")
    e=e[e.transcriptomics_sample_id.astype(str).isin(g.columns)].drop_duplicates("transcriptomics_sample_id").copy()
    e.index=e.transcriptomics_sample_id.astype(str);cells=[c for c in e.index if c in g.columns]
    e=e.loc[cells];g=g[cells]
    Y=e[[t for t in TARGETS if t in e.columns]].apply(pd.to_numeric,errors="coerce")
    ok=Y.notna().all(axis=1);Y=Y.loc[ok];e=e.loc[ok];g=g[e.index]
    X=g.apply(pd.to_numeric,errors="coerce").fillna(0).rank(axis=0,pct=True).T
    return X,Y,e["_subject"].astype(str).to_numpy()

def eval_split(X,Y,splits,groups=None,seed=42,permute=False):
    Xv=X.to_numpy(float);Yv=Y.to_numpy(float);rows=[];rng=np.random.default_rng(seed)
    for fold,(tr,te) in enumerate(splits,1):
        var=np.nanvar(Xv[tr],axis=0);sel=np.argsort(var)[-min(300,len(var)):]
        ytr=Yv[tr].copy()
        if permute:
            ytr=ytr[rng.permutation(len(ytr))]
        model=ExtraTreesRegressor(n_estimators=120,max_features="sqrt",min_samples_leaf=4,n_jobs=-1,random_state=seed+fold)
        model.fit(Xv[tr][:,sel],ytr);p=model.predict(Xv[te][:,sel])
        for j,t in enumerate(Y.columns):
            rho=spearmanr(Yv[te,j],p[:,j]).statistic
            rows.append({"fold":fold,"target":t,"spearman":float(rho),"r2":float(r2_score(Yv[te,j],p[:,j]))})
    return pd.DataFrame(rows)

def main():
    X,Y,groups=load()
    grouped=list(GroupKFold(5).split(X,Y,groups))
    naive=list(KFold(5,shuffle=True,random_state=42).split(X,Y))
    rg=eval_split(X,Y,grouped,groups,seed=100,permute=False);rg["experiment"]="grouped_real"
    rn=eval_split(X,Y,naive,None,seed=200,permute=False);rn["experiment"]="naive_random_real"

    perms=[]
    for i in range(8):
        x=eval_split(X,Y,grouped,groups,seed=1000+i,permute=True);x["experiment"]=f"grouped_permuted_{i+1}";perms.append(x)
    rp=pd.concat(perms,ignore_index=True)
    allr=pd.concat([rg,rn,rp],ignore_index=True);allr.to_csv(DATA/"ml_negative_control_folds.csv",index=False)

    summary=allr.groupby(["experiment","target"]).agg(mean_spearman=("spearman","mean"),mean_r2=("r2","mean")).reset_index()
    summary.to_csv(DATA/"ml_negative_control_summary.csv",index=False)
    real=summary[summary.experiment=="grouped_real"].set_index("target")
    naiveS=summary[summary.experiment=="naive_random_real"].set_index("target")
    permS=summary[summary.experiment.str.startswith("grouped_permuted")].groupby("target").mean(numeric_only=True)
    comps=[]
    for t in real.index:
        comps.append({
          "target":t,
          "grouped_spearman":float(real.loc[t,"mean_spearman"]),
          "naive_random_spearman":float(naiveS.loc[t,"mean_spearman"]),
          "leakage_inflation_delta":float(naiveS.loc[t,"mean_spearman"]-real.loc[t,"mean_spearman"]),
          "permuted_mean_spearman":float(permS.loc[t,"mean_spearman"]),
          "signal_over_null_delta":float(real.loc[t,"mean_spearman"]-permS.loc[t,"mean_spearman"])
        })
    payload={
      "nCells":len(X),"nSubjects":len(set(groups)),"permutations":8,
      "comparisons":comps,
      "guardrail":"Naive random split is included only as a leakage diagnostic. Grouped split is the valid evaluation."
    }
    (DATA/"ml_negative_controls.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    print(json.dumps(comps[:5],indent=2))
if __name__=="__main__":main()
