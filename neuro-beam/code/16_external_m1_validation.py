"""External M1 validation for NEURO-BEAM transcriptome -> electrophysiology models.

Discovery/training: Allen visual cortex Patch-seq (same-cell ephys + RNA).
External test: Scala et al. motor-cortex Patch-seq.

To reduce cross-platform scale mismatch, expression is standardized per gene
within each dataset and electrical outcomes are standardized per trait within
each dataset. M1 outcomes are never used for fitting or feature selection.
"""
from __future__ import annotations
import re,json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score,mean_absolute_error

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"

VBASE="https://raw.githubusercontent.com/daifengwanglab/scMNC/main/mouse_visual_cortex/data/"
MBASE="https://raw.githubusercontent.com/berenslab/mini-atlas/master/data/"

MAP={
 "vrest":"Resting membrane potential (mV)",
 "ri":"Input resistance (MOhm)",
 "sag":"Sag ratio",
 "tau":"Membrane time constant (ms)",
 "adaptation":"Spike frequency adaptation",
 "latency":"Latency (ms)",
 "upstroke_downstroke_ratio_long_square":"Upstroke-to-downstroke ratio",
 "threshold_i_long_square":"Rheobase (pA)"
}

def session(v):
    t=re.findall(r"\d+",str(v));return t[1] if len(t)>=2 else None

def load_v1():
    e=pd.read_csv(VBASE+"efeature.csv")
    g=pd.read_csv(VBASE+"geneExp_filtered.csv")
    m=pd.read_csv(VBASE+"20200711_patchseq_metadata_mouse.csv")
    e["_session"]=e["ID"].map(session).astype(str)
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
    return X,e

def load_m1():
    meta=pd.read_csv(MBASE+"m1_patchseq_meta_data.csv",sep="\t")
    eph=pd.read_csv(MBASE+"m1_patchseq_ephys_features.csv")
    ex=pd.read_csv(MBASE+"m1_patchseq_exon_counts.csv.gz",compression="gzip")
    intr=pd.read_csv(MBASE+"m1_patchseq_intron_counts.csv.gz",compression="gzip")
    gene_col=ex.columns[0]
    ex=ex.set_index(gene_col);intr=intr.set_index(intr.columns[0])
    common_idx=ex.index.intersection(intr.index)
    counts=ex.loc[common_idx].apply(pd.to_numeric,errors="coerce").fillna(0)+intr.loc[common_idx].apply(pd.to_numeric,errors="coerce").fillna(0)
    counts.columns=[str(c)[1:] if str(c).startswith("X") else str(c) for c in counts.columns]
    lib=counts.sum(axis=0).replace(0,np.nan)
    cpm=counts.divide(lib,axis=1)*1e6
    X=np.log1p(cpm).T
    cell_col="cell id" if "cell id" in eph.columns else eph.columns[0]
    eph=eph.set_index(eph[cell_col].astype(str))
    meta_cells=set(meta["Cell"].astype(str))
    cells=[c for c in X.index.astype(str) if c in eph.index and c in meta_cells]
    return X.loc[cells],eph.loc[cells]

def z_by_dataset(df):
    mu=df.mean(axis=0);sd=df.std(axis=0).replace(0,np.nan)
    return (df-mu)/sd

def z_series(s):
    s=pd.to_numeric(s,errors="coerce");return (s-s.mean())/s.std()

def main():
    Xv,Ev=load_v1();Xm,Em=load_m1()
    shared=sorted(set(Xv.columns).intersection(Xm.columns))
    if len(shared)<500: raise RuntimeError(f"Only {len(shared)} shared genes")
    Xv=Xv[shared].replace([np.inf,-np.inf],np.nan).fillna(0)
    Xm=Xm[shared].replace([np.inf,-np.inf],np.nan).fillna(0)
    Xvz=z_by_dataset(Xv).fillna(0);Xmz=z_by_dataset(Xm).fillna(0)

    top_mouse=None
    p=DATA/"top500_gene_catalog.csv"
    if p.exists():
        cat=pd.read_csv(p)
        top_mouse=[g for g in cat.get("mouse_gene",pd.Series(dtype=str)).astype(str) if g in shared]
        if len(top_mouse)<50: top_mouse=None

    rows=[]
    for vf,mf in MAP.items():
        if vf not in Ev.columns or mf not in Em.columns: continue
        yv=z_series(Ev[vf]);ym=z_series(Em[mf])
        tv=yv.notna();tm=ym.notna()
        for name,genes in [("ridge_shared_all",shared),("ridge_cbe_top500",top_mouse)]:
            if not genes: continue
            model=Ridge(alpha=100.0)
            model.fit(Xvz.loc[tv,genes],yv.loc[tv])
            pred=model.predict(Xmz.loc[tm,genes])
            obs=ym.loc[tm].to_numpy(float)
            rho=spearmanr(obs,pred,nan_policy="omit").statistic
            rows.append({
              "model":name,"v1_trait":vf,"m1_trait":mf,
              "n_train":int(tv.sum()),"n_external":int(tm.sum()),"n_genes":len(genes),
              "external_r2":float(r2_score(obs,pred)),
              "external_mae_z":float(mean_absolute_error(obs,pred)),
              "external_spearman":float(rho) if np.isfinite(rho) else None
            })
    res=pd.DataFrame(rows)
    res.to_csv(DATA/"external_m1_validation.csv",index=False)
    summary=res.groupby("model").agg(
      mean_external_r2=("external_r2","mean"),
      mean_external_spearman=("external_spearman","mean"),
      median_external_spearman=("external_spearman","median"),
      mean_external_mae_z=("external_mae_z","mean"),
      traits=("v1_trait","count")
    ).reset_index()
    payload={
      "discoveryRegion":"visual cortex","externalRegion":"motor cortex",
      "expressionHarmonization":"per-gene within-dataset z-standardization after log transform/CPM",
      "outcomeHarmonization":"within-dataset z-standardization per electrical trait",
      "models":summary.to_dict(orient="records"),"perTrait":res.to_dict(orient="records"),
      "guardrail":"External M1 outcomes are not used during V1 fitting or feature selection; standardization uses only within-dataset marginal distributions."
    }
    (DATA/"external_m1_validation.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    print(json.dumps(payload["models"],indent=2))

if __name__=="__main__":main()
