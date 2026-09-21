"""NEURO-BEAM state stability and biological validation.

This script:
1) reuses physiology-only features from the visual-cortex discovery dataset,
2) evaluates K-means, Gaussian mixture and HDBSCAN structure,
3) estimates bootstrap/resampling stability of the provisional five-state solution,
4) only after freezing electrical labels reveals known transcriptomic class labels,
5) reports ARI/NMI, contingency tables and state-by-class enrichment.

No transcriptomic label is used to create electrical states.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from scipy.stats import chi2_contingency
from sklearn.preprocessing import RobustScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, HDBSCAN
from sklearn.mixture import GaussianMixture
from sklearn.metrics import (
    silhouette_score, adjusted_rand_score, normalized_mutual_info_score
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data"
OUT.mkdir(parents=True,exist_ok=True)

E_URL="https://raw.githubusercontent.com/daifengwanglab/scMNC/main/mouse_visual_cortex/data/efeature_filtered.csv"
M_URL="https://raw.githubusercontent.com/daifengwanglab/scMNC/main/mouse_visual_cortex/data/20200711_patchseq_metadata_mouse.csv"

EXCLUDE_EXACT={"rheobase_sweep_num","thumbnail_sweep_num"}
EXCLUDE_PREFIXES=("threshold_t_","peak_t_","trough_t_","fast_trough_t_")

def choose_id_column(df):
    preferred=["transcriptomics_sample_id","cell_id","cell id","ID","id"]
    for c in preferred:
        if c in df.columns:
            return c
    first=df.columns[0]
    if str(first).lower().startswith("unnamed") or df[first].dtype=="object":
        return first
    return None

def prep_ephys(e):
    idcol=choose_id_column(e)
    ids=e[idcol].astype(str).copy() if idcol else pd.Series(np.arange(len(e)).astype(str))
    num=e.select_dtypes(include=[np.number]).copy()
    exclude=[c for c in num.columns if c in EXCLUDE_EXACT or any(c.startswith(p) for p in EXCLUDE_PREFIXES)]
    num=num.drop(columns=exclude,errors="ignore")
    num=num.loc[:,num.isna().mean()<=0.20]
    num=num.loc[:,num.nunique(dropna=True)>1]
    keep=num.isna().mean(axis=1)<=0.20
    num=num.loc[keep].reset_index(drop=True)
    ids=ids.loc[keep].reset_index(drop=True)
    num=num.fillna(num.median(numeric_only=True))
    X=RobustScaler().fit_transform(num)
    pca=PCA(n_components=min(10,X.shape[1],X.shape[0]-1),random_state=42)
    pcs=pca.fit_transform(X)
    return ids,num,pcs,exclude,idcol,pca

def align_labels(base, other):
    # Map other cluster labels onto base labels by maximizing overlap.
    bvals=np.unique(base)
    ovals=np.unique(other)
    valid_o=[o for o in ovals if o!=-1]
    if not valid_o:
        return np.full_like(other,-1)
    mat=np.zeros((len(bvals),len(valid_o)),dtype=int)
    for i,b in enumerate(bvals):
        for j,o in enumerate(valid_o):
            mat[i,j]=np.sum((base==b)&(other==o))
    ri,ci=linear_sum_assignment(-mat)
    mapping={valid_o[c]:bvals[r] for r,c in zip(ri,ci)}
    return np.array([mapping.get(x,-1) for x in other])

def cluster_jaccard(base, aligned, k):
    vals=[]
    for c in range(k):
        a=base==c
        b=aligned==c
        union=np.sum(a|b)
        vals.append(float(np.sum(a&b)/union) if union else np.nan)
    return vals

def main():
    e=pd.read_csv(E_URL)
    m=pd.read_csv(M_URL)
    ids,num,pcs,excluded,idcol,pca=prep_ephys(e)
    use=pcs[:,:min(8,pcs.shape[1])]

    # Freeze baseline k=5, matching the corrected discovery run.
    k=5
    km=KMeans(n_clusters=k,n_init=100,random_state=42)
    base=km.fit_predict(use)

    # Gaussian mixture model comparison.
    gmm_rows=[]
    best_gmm=None
    for kk in range(2,9):
        g=GaussianMixture(n_components=kk,covariance_type="full",n_init=5,random_state=42,reg_covar=1e-6)
        lab=g.fit_predict(use)
        gmm_rows.append({
            "k":kk,
            "bic":float(g.bic(use)),
            "aic":float(g.aic(use)),
            "silhouette":float(silhouette_score(use,lab)) if len(np.unique(lab))>1 else None
        })
    best_k_bic=int(min(gmm_rows,key=lambda x:x["bic"])["k"])
    g=GaussianMixture(n_components=best_k_bic,covariance_type="full",n_init=10,random_state=42,reg_covar=1e-6)
    gmm_labels=g.fit_predict(use)

    # HDBSCAN density-based structure, conservative default.
    h=HDBSCAN(min_cluster_size=max(25,int(len(use)*0.01)),min_samples=10,cluster_selection_method="eom")
    hlabels=h.fit_predict(use)
    h_clusters=int(len(set(hlabels))- (1 if -1 in hlabels else 0))
    h_noise=float(np.mean(hlabels==-1))

    # Bootstrap/resampling stability. Fit on 80%, assign all neurons to centers.
    rng=np.random.default_rng(20260921)
    ari_runs=[]
    jacc_runs=[]
    n_iter=200
    for _ in range(n_iter):
        idx=rng.choice(len(use),size=int(len(use)*0.80),replace=False)
        model=KMeans(n_clusters=k,n_init=30,random_state=int(rng.integers(0,2**31-1))).fit(use[idx])
        pred=model.predict(use)
        aligned=align_labels(base,pred)
        ari_runs.append(float(adjusted_rand_score(base,aligned)))
        jacc_runs.append(cluster_jaccard(base,aligned,k))
    jacc_arr=np.array(jacc_runs,dtype=float)
    stability={
        f"E{i+1}":{
            "mean_jaccard":float(np.nanmean(jacc_arr[:,i])),
            "p05":float(np.nanquantile(jacc_arr[:,i],0.05)),
            "p95":float(np.nanquantile(jacc_arr[:,i],0.95)),
            "n":int(np.sum(base==i))
        } for i in range(k)
    }

    # Reveal biological labels only now.
    meta_id="transcriptomics_sample_id" if "transcriptomics_sample_id" in m.columns else choose_id_column(m)
    broad=None
    if "t_type" in m.columns:
        broad=m["t_type"].fillna("").astype(str).str.split().str[0]
    elif "cell_subclass" in m.columns:
        broad=m["cell_subclass"].fillna("").astype(str)
    elif "subclass_label" in m.columns:
        broad=m["subclass_label"].fillna("").astype(str)
    else:
        broad=pd.Series([""]*len(m))

    md=pd.DataFrame({"cell_id":m[meta_id].astype(str),"class":broad})
    state_df=pd.DataFrame({"cell_id":ids.astype(str),"state_num":base,"state":[f"E{x+1}" for x in base]})
    merged=state_df.merge(md,on="cell_id",how="left")
    merged["class"]=merged["class"].replace({"":"Unknown"}).fillna("Unknown")
    known=merged[merged["class"]!="Unknown"].copy()

    contingency=pd.crosstab(known["state"],known["class"])
    if contingency.shape[0]>1 and contingency.shape[1]>1:
        chi2,pval,dof,_=chi2_contingency(contingency)
    else:
        chi2,pval,dof=np.nan,np.nan,0

    # Encode class labels for ARI/NMI.
    class_codes=pd.Categorical(known["class"]).codes
    state_codes=pd.Categorical(known["state"]).codes
    ari_bio=float(adjusted_rand_score(class_codes,state_codes)) if len(known)>1 else None
    nmi_bio=float(normalized_mutual_info_score(class_codes,state_codes)) if len(known)>1 else None

    # Enrichment as observed / expected frequency.
    total=len(known)
    rown=contingency.sum(axis=1)
    coln=contingency.sum(axis=0)
    enrich={}
    for st in contingency.index:
        enrich[st]={}
        for cl in contingency.columns:
            obs=float(contingency.loc[st,cl])
            exp=float(rown[st]*coln[cl]/total) if total else np.nan
            enrich[st][cl]=float(obs/exp) if exp>0 else None

    out={
        "status":"computed",
        "n_neurons":int(len(use)),
        "n_features":int(num.shape[1]),
        "excluded_protocol_timing_features":excluded,
        "baseline_k":k,
        "baseline_cluster_sizes":{f"E{i+1}":int(np.sum(base==i)) for i in range(k)},
        "bootstrap_iterations":n_iter,
        "bootstrap_ari_mean":float(np.mean(ari_runs)),
        "bootstrap_ari_p05":float(np.quantile(ari_runs,0.05)),
        "bootstrap_ari_p95":float(np.quantile(ari_runs,0.95)),
        "state_stability":stability,
        "gmm_comparison":gmm_rows,
        "gmm_best_k_bic":best_k_bic,
        "gmm_vs_kmeans_ari":float(adjusted_rand_score(base,gmm_labels)),
        "hdbscan_clusters":h_clusters,
        "hdbscan_noise_fraction":h_noise,
        "hdbscan_vs_kmeans_ari_nonnoise":float(adjusted_rand_score(base[hlabels!=-1],hlabels[hlabels!=-1])) if np.any(hlabels!=-1) else None,
        "label_reveal_n":int(len(known)),
        "biological_classes":{str(k):int(v) for k,v in known["class"].value_counts().to_dict().items()},
        "state_class_ari":ari_bio,
        "state_class_nmi":nmi_bio,
        "state_class_chi2":None if np.isnan(chi2) else float(chi2),
        "state_class_p":None if np.isnan(pval) else float(pval),
        "state_class_dof":int(dof),
        "contingency":{st:{cl:int(contingency.loc[st,cl]) for cl in contingency.columns} for st in contingency.index},
        "enrichment_observed_over_expected":enrich,
        "interpretation_guardrail":"Electrical states were created without biological labels. Biological correspondence is descriptive/associational, not causal."
    }
    (OUT/"visual_cortex_stability_validation.json").write_text(json.dumps(out,indent=2))
    merged.to_csv(OUT/"visual_cortex_state_labels_revealed.csv",index=False)
    print(json.dumps({
        "n_neurons":out["n_neurons"],
        "bootstrap_ari_mean":out["bootstrap_ari_mean"],
        "gmm_best_k_bic":out["gmm_best_k_bic"],
        "hdbscan_clusters":out["hdbscan_clusters"],
        "state_class_ari":out["state_class_ari"],
        "state_class_nmi":out["state_class_nmi"]
    },indent=2))

if __name__=="__main__":
    main()
