"""CBEF-guided multi-task latent electrophysiology model.

Tests whether a cross-domain CBEF prior improves multi-output prediction beyond
the same latent learner with unweighted, bioelectric-only, or cancer-only gene
priors. Subject-grouped outer cross-validation prevents cell-level leakage.

The prior rescales standardized gene features before PLS latent-factor learning.
"""
from __future__ import annotations
import json,re
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.cross_decomposition import PLSRegression
from sklearn.metrics import r2_score,mean_absolute_error

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
BASE="https://raw.githubusercontent.com/daifengwanglab/scMNC/main/mouse_visual_cortex/data/"
E_URL=BASE+"efeature.csv";G_URL=BASE+"geneExp_filtered.csv";M_URL=BASE+"20200711_patchseq_metadata_mouse.csv"
TRAITS=["vrest","ri","sag","tau","f_i_curve_slope","adaptation","latency","avg_isi",
"upstroke_downstroke_ratio_long_square","peak_v_long_square","trough_v_long_square","fast_trough_v_long_square",
"threshold_v_long_square","threshold_i_long_square","threshold_v_short_square","threshold_i_short_square",
"threshold_v_ramp","threshold_i_ramp"]

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
    e=e.loc[cells];g=g[cells]
    X=g.T.apply(pd.to_numeric,errors="coerce")
    if np.nanmin(X.to_numpy(float))>=0:X=np.log1p(X)
    Y=e[[t for t in TRAITS if t in e.columns]].apply(pd.to_numeric,errors="coerce")
    valid=Y.notna().all(axis=1)
    return X.loc[valid],Y.loc[valid],e.loc[valid,"_subject"].astype(str)

def evaluate(Y,pred):
    out=[]
    for j,t in enumerate(Y.columns):
        y=Y.iloc[:,j].to_numpy(float);p=pred[:,j]
        rho=spearmanr(y,p,nan_policy="omit").statistic
        out.append({"trait":t,"r2":float(r2_score(y,p)),
                    "mae":float(mean_absolute_error(y,p)),
                    "spearman":float(rho) if np.isfinite(rho) else None})
    return out

def main():
    X,Y,groups=load()
    cat=pd.read_csv(DATA/"top500_gene_catalog.csv")
    cat=cat[cat["mouse_gene"].astype(str).isin(X.columns)].drop_duplicates("mouse_gene").copy()
    if len(cat)<300:raise RuntimeError(f"Insufficient CBEF genes shared with expression matrix: {len(cat)}")
    cat=cat.head(500)
    genes=cat["mouse_gene"].astype(str).tolist()
    X=X[genes].replace([np.inf,-np.inf],np.nan)

    priors={
      "latent_unweighted":np.ones(len(genes)),
      "latent_bioelectric_prior":0.10+0.90*cat["bioelectric_evidence_score"].to_numpy(float),
      "latent_cancer_prior":0.10+0.90*cat["cancer_evidence_score"].to_numpy(float),
      "latent_cbef_prior":0.10+0.90*cat["cbef_discovery_score"].to_numpy(float)
    }
    gkf=GroupKFold(n_splits=5);rows=[]
    for fold,(tr,te) in enumerate(gkf.split(X,Y,groups),1):
        Xtr,Xte=X.iloc[tr],X.iloc[te];Ytr,Yte=Y.iloc[tr],Y.iloc[te]
        # Training-fold-only imputation and scaling.
        med=Xtr.median()
        Xtr=Xtr.fillna(med);Xte=Xte.fillna(med)
        xs=StandardScaler().fit(Xtr);ys=StandardScaler().fit(Ytr)
        ZXtr=xs.transform(Xtr);ZXte=xs.transform(Xte)
        ZYtr=ys.transform(Ytr)

        for name,w in priors.items():
            sw=np.sqrt(np.clip(w,0.05,None))
            model=PLSRegression(n_components=min(20,ZYtr.shape[1]+2),scale=False,max_iter=500)
            model.fit(ZXtr*sw,ZYtr)
            zpred=np.asarray(model.predict(ZXte*sw))
            pred=ys.inverse_transform(zpred)
            for r in evaluate(Yte,pred):
                r.update({"fold":fold,"model":name,"n_genes":len(genes),
                          "n_train":len(tr),"n_test":len(te),
                          "n_groups_train":groups.iloc[tr].nunique(),"n_groups_test":groups.iloc[te].nunique()})
                rows.append(r)

    res=pd.DataFrame(rows);res.to_csv(DATA/"cbef_multitask_folds.csv",index=False)
    trait=res.groupby(["model","trait"]).agg(
      mean_r2=("r2","mean"),sd_r2=("r2","std"),
      mean_spearman=("spearman","mean"),mean_mae=("mae","mean"),folds=("fold","count")
    ).reset_index()
    trait.to_csv(DATA/"cbef_multitask_trait_summary.csv",index=False)
    overall=trait.groupby("model").agg(
      mean_trait_r2=("mean_r2","mean"),median_trait_r2=("mean_r2","median"),
      mean_trait_spearman=("mean_spearman","mean"),mean_trait_mae=("mean_mae","mean"),traits=("trait","count")
    ).reset_index().sort_values("mean_trait_r2",ascending=False)
    payload={
      "modelName":"CBEF-guided multi-task latent regression",
      "nCells":len(X),"nGenes":len(genes),"nSubjects":groups.nunique(),"traits":list(Y.columns),
      "models":overall.to_dict(orient="records"),"perTrait":trait.to_dict(orient="records"),
      "priorDefinition":"standardized gene features multiplied by sqrt(0.10 + 0.90*evidence_score) before PLS latent-factor learning",
      "guardrail":"CBEF priors are fixed before each grouped CV fit; imputation and standardization are training-fold-only."
    }
    (DATA/"cbef_multitask_benchmark.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    print(json.dumps(payload["models"],indent=2))

if __name__=="__main__":main()
