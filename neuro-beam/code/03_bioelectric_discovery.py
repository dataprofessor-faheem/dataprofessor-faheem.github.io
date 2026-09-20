"""Baseline electrophysiology-only bioelectric-state discovery."""
from pathlib import Path
import json, numpy as np, pandas as pd
from sklearn.preprocessing import RobustScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score,calinski_harabasz_score,davies_bouldin_score
ROOT=Path(__file__).resolve().parents[1]; INFILE=ROOT/"data"/"processed"/"ephys_features.csv"; OUT=ROOT/"results"/"bioelectric_discovery"; OUT.mkdir(parents=True,exist_ok=True)
NON_FEATURE={"specimen_id","donor_id","dataset_id","cell_class","cell_subclass","t_type","MET_type","brain_region","cortical_layer","sex","age"}
def main():
    df=pd.read_csv(INFILE)
    feature_cols=[c for c in df.columns if c not in NON_FEATURE and pd.api.types.is_numeric_dtype(df[c])]
    X=df[feature_cols].replace([np.inf,-np.inf],np.nan); X=X.fillna(X.median(numeric_only=True)); Xz=RobustScaler().fit_transform(X)
    pca=PCA(n_components=min(20,Xz.shape[1],Xz.shape[0]-1),random_state=42); pcs=pca.fit_transform(Xz)
    pd.DataFrame(pcs,columns=[f"PC{i+1}" for i in range(pcs.shape[1])]).to_csv(OUT/"pca_scores.csv",index=False)
    pd.DataFrame({"feature":feature_cols,**{f"PC{i+1}":pca.components_[i] for i in range(pca.components_.shape[0])}}).to_csv(OUT/"pca_loadings.csv",index=False)
    rows=[]; use=pcs[:,:min(10,pcs.shape[1])]; max_k=min(12,max(2,len(df)-1))
    for k in range(2,max_k+1):
        labels=KMeans(n_clusters=k,n_init=50,random_state=42).fit_predict(use)
        rows.append({"k":k,"silhouette":silhouette_score(use,labels),"calinski_harabasz":calinski_harabasz_score(use,labels),"davies_bouldin":davies_bouldin_score(use,labels)})
    ev=pd.DataFrame(rows); ev.to_csv(OUT/"cluster_diagnostics_baseline.csv",index=False)
    best_k=int(ev.sort_values(["silhouette","calinski_harabasz"],ascending=[False,False]).iloc[0]["k"])
    final=KMeans(n_clusters=best_k,n_init=100,random_state=42).fit_predict(use)
    a=df[[c for c in ["dataset_id","specimen_id","donor_id"] if c in df.columns]].copy(); a["bioelectric_state_baseline"]=[f"E{x+1}" for x in final]; a.to_csv(OUT/"bioelectric_state_assignments_baseline.csv",index=False)
    with open(OUT/"run_summary.json","w") as f: json.dump({"n_neurons":len(df),"n_features":len(feature_cols),"best_k_baseline":best_k,"note":"K-means is baseline only; final states require GMM/HDBSCAN/consensus and bootstrap/donor stability."},f,indent=2)
if __name__=="__main__": main()