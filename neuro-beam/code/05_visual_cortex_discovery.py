"""NEURO-BEAM visual-cortex bioelectric discovery.
Downloads the public processed visual-cortex Patch-seq electrophysiology/metadata
used by the scMNC companion repository, performs QC, robust scaling, PCA and
baseline cluster diagnostics, and writes dashboard-ready JSON/CSV outputs.
This baseline does NOT use transcriptomic labels to define electrical states.
"""
from __future__ import annotations
import json, os, math
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data"
OUT.mkdir(parents=True,exist_ok=True)

E_URL="https://raw.githubusercontent.com/daifengwanglab/scMNC/main/mouse_visual_cortex/data/efeature_filtered.csv"
M_URL="https://raw.githubusercontent.com/daifengwanglab/scMNC/main/mouse_visual_cortex/data/20200711_patchseq_metadata_mouse.csv"

def read_source(url:str)->pd.DataFrame:
    return pd.read_csv(url)

def choose_id(df:pd.DataFrame):
    preferred=["ID","id","cell_id","cell id","transcriptomics_sample_id","session_idg"]
    for c in preferred:
        if c in df.columns:
            return c
    first=df.columns[0]
    if str(first).lower().startswith("unnamed") or df[first].dtype=="object":
        return first
    return None

def main():
    e=read_source(E_URL)
    m=read_source(M_URL)
    idcol=choose_id(e)
    ids=e[idcol].astype(str) if idcol else pd.Series(np.arange(len(e)).astype(str),name="row_id")

    # Numeric-only electrophysiology; labels/IDs never enter the discovery matrix.
    num=e.select_dtypes(include=[np.number]).copy()

    # Exclude acquisition/protocol bookkeeping and absolute event-time columns.
    # These can dominate PCA despite carrying little biological information.
    exclude_exact={"rheobase_sweep_num","thumbnail_sweep_num"}
    exclude_substrings=("_sweep_num",)
    exclude_prefixes=("threshold_t_","peak_t_","trough_t_","fast_trough_t_")
    exclude_cols=[
        c for c in num.columns
        if c in exclude_exact
        or any(x in c for x in exclude_substrings)
        or any(c.startswith(p) for p in exclude_prefixes)
    ]
    num=num.drop(columns=exclude_cols,errors="ignore")

    # Remove high-missing and constant/near-constant features.
    miss=num.isna().mean()
    num=num.loc[:,miss<=0.20]
    nunique=num.nunique(dropna=True)
    num=num.loc[:,nunique>1]

    row_missing=num.isna().mean(axis=1)
    keep=row_missing<=0.20
    num=num.loc[keep].copy()
    ids=ids.loc[keep].reset_index(drop=True)
    num=num.reset_index(drop=True)
    med=num.median(numeric_only=True)
    num=num.fillna(med)

    # Robust scale to reduce sensitivity to heavy-tailed electrophysiology measures.
    X=RobustScaler().fit_transform(num)
    ncomp=min(10,X.shape[1],X.shape[0]-1)
    pca=PCA(n_components=ncomp,random_state=42)
    pcs=pca.fit_transform(X)

    # K-means is only a baseline diagnostic; final states require consensus/GMM/HDBSCAN
    # and bootstrap/donor stability, as pre-specified.
    eval_rows=[]
    label_by_k={}
    rng=np.random.default_rng(42)
    use=pcs[:,:min(8,ncomp)]
    for k in range(2,min(10,len(use)-1)+1):
        model=KMeans(n_clusters=k,n_init=50,random_state=42)
        labels=model.fit_predict(use)
        label_by_k[k]=labels
        # Cohort is small enough for full-cohort validity metrics; this also
        # prevents rare clusters disappearing from a random metric subsample.
        unique=np.unique(labels)
        if len(unique)<2:
            continue
        eval_rows.append({
            "k":k,
            "silhouette":float(silhouette_score(use,labels)),
            "calinski_harabasz":float(calinski_harabasz_score(use,labels)),
            "davies_bouldin":float(davies_bouldin_score(use,labels))
        })
    ev=pd.DataFrame(eval_rows)
    best_k=int(ev.sort_values(["silhouette","calinski_harabasz"],ascending=[False,False]).iloc[0]["k"])
    labels=label_by_k[best_k]

    # PCA loadings and cluster profiles.
    load=pd.DataFrame(pca.components_.T,index=num.columns,columns=[f"PC{i+1}" for i in range(ncomp)])
    top_loadings={}
    for pc in ["PC1","PC2","PC3"][:ncomp]:
        s=load[pc].abs().sort_values(ascending=False).head(8)
        top_loadings[pc]=[{"feature":str(f),"loading":float(load.loc[f,pc])} for f in s.index]

    prof=pd.DataFrame(num)
    prof["state"]=[f"E{x+1}" for x in labels]
    cluster_sizes=prof["state"].value_counts().sort_index().to_dict()
    profile_cols=list(num.columns[:min(20,len(num.columns))])
    cluster_profiles=prof.groupby("state")[profile_cols].median().round(5).to_dict(orient="index")

    # Sample PCA coordinates for browser rendering.
    plot_idx=np.arange(len(pcs))
    if len(plot_idx)>1800:
        plot_idx=rng.choice(plot_idx,1800,replace=False)
    plot=pd.DataFrame({
        "cell_id":ids.iloc[plot_idx].astype(str).values,
        "PC1":pcs[plot_idx,0],
        "PC2":pcs[plot_idx,1] if ncomp>1 else 0,
        "state":[f"E{x+1}" for x in labels[plot_idx]]
    })
    plot.to_csv(OUT/"visual_cortex_pca_sample.csv",index=False)
    ev.to_csv(OUT/"visual_cortex_cluster_diagnostics.csv",index=False)

    result={
        "status":"computed",
        "source_ephys":E_URL,
        "source_metadata":M_URL,
        "source_repository":"https://github.com/daifengwanglab/scMNC",
        "analysis_role":"discovery",
        "raw_ephys_rows":int(len(e)),
        "metadata_rows":int(len(m)),
        "qc_neurons":int(len(num)),
        "numeric_features_input":int(e.select_dtypes(include=[np.number]).shape[1]),
        "excluded_protocol_timing_features":exclude_cols,
        "numeric_features_after_qc":int(num.shape[1]),
        "pca_components":int(ncomp),
        "explained_variance_first3":[float(x) for x in pca.explained_variance_ratio_[:3]],
        "explained_variance_total":float(pca.explained_variance_ratio_.sum()),
        "baseline_best_k":best_k,
        "cluster_sizes":{str(k):int(v) for k,v in cluster_sizes.items()},
        "cluster_diagnostics":eval_rows,
        "top_loadings":top_loadings,
        "cluster_profile_features":profile_cols,
        "cluster_profiles":cluster_profiles,
        "method_note":"K-means/PCA are baseline discovery diagnostics only. Protocol bookkeeping/absolute event-time variables are excluded. Final bioelectric states require GMM/HDBSCAN/consensus, bootstrap stability and donor-aware validation before biological naming.",
        "label_blinding":"Known transcriptomic/cell-type labels were not used to define baseline electrical states."
    }
    (OUT/"visual_cortex_discovery.json").write_text(json.dumps(result,indent=2))
    print(json.dumps({k:result[k] for k in ["raw_ephys_rows","metadata_rows","qc_neurons","numeric_features_after_qc","baseline_best_k","cluster_sizes"]},indent=2))

if __name__=="__main__":
    main()
