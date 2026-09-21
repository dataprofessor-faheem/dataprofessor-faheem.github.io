"""BEAM-Factor: shared-gene multi-view latent factorization.

Jointly models:
  E: gene x electrophysiology association matrix (signed Spearman rho)
  C: gene x cancer-cohort mutation-prevalence matrix

The model learns a shared gene embedding U with separate view decoders.
Cancer evidence is never interpreted as a causal neuronal effect.

Evaluation:
1) masked-entry reconstruction for E and C across alpha/rank settings;
2) external M1 reproducibility of gene-electrophysiology association patterns.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
BIO=DATA/"top500_bioelectric_matrix.csv"
CAN=DATA/"top500_cancer_matrix.csv"
MBASE="https://raw.githubusercontent.com/berenslab/mini-atlas/master/data/"

M1_MAP={
 "vrest":"Resting membrane potential (mV)",
 "ri":"Input resistance (MOhm)",
 "sag":"Sag ratio",
 "tau":"Membrane time constant (ms)",
 "adaptation":"Spike frequency adaptation",
 "latency":"Latency (ms)",
 "upstroke_downstroke_ratio_long_square":"Upstroke-to-downstroke ratio",
 "threshold_i_long_square":"Rheobase (pA)"
}

def zcols(x):
    x=np.asarray(x,float)
    mu=np.nanmean(x,axis=0);sd=np.nanstd(x,axis=0)
    sd=np.where(sd<1e-9,1.0,sd)
    return (x-mu)/sd,mu,sd

def als_factorize(X,mask,k=8,lam=.8,n_iter=30,seed=42):
    rng=np.random.default_rng(seed)
    n,m=X.shape
    U=rng.normal(0,.1,size=(n,k));V=rng.normal(0,.1,size=(m,k))
    I=np.eye(k)
    for _ in range(n_iter):
        for i in range(n):
            obs=np.where(mask[i])[0]
            if not len(obs):continue
            A=V[obs].T@V[obs]+lam*I
            b=V[obs].T@X[i,obs]
            U[i]=np.linalg.solve(A,b)
        for j in range(m):
            obs=np.where(mask[:,j])[0]
            if not len(obs):continue
            A=U[obs].T@U[obs]+lam*I
            b=U[obs].T@X[obs,j]
            V[j]=np.linalg.solve(A,b)
    return U,V,U@V.T

def holdout_mask(shape,frac,rng,base_mask=None):
    mask=np.ones(shape,bool) if base_mask is None else base_mask.copy()
    test=np.zeros(shape,bool)
    # sample per column so every trait/cohort is evaluated
    for j in range(shape[1]):
        candidates=np.where(mask[:,j])[0]
        n=max(1,int(len(candidates)*frac))
        chosen=rng.choice(candidates,size=n,replace=False)
        mask[chosen,j]=False;test[chosen,j]=True
    return mask,test

def rmse(a,b):
    return float(np.sqrt(np.mean((np.asarray(a)-np.asarray(b))**2)))

def load_m1_assoc(mouse_genes):
    meta=pd.read_csv(MBASE+"m1_patchseq_meta_data.csv",sep="\t")
    eph=pd.read_csv(MBASE+"m1_patchseq_ephys_features.csv")
    ex=pd.read_csv(MBASE+"m1_patchseq_exon_counts.csv.gz",compression="gzip")
    intr=pd.read_csv(MBASE+"m1_patchseq_intron_counts.csv.gz",compression="gzip")
    ex=ex.set_index(ex.columns[0]);intr=intr.set_index(intr.columns[0])
    ix=ex.index.intersection(intr.index)
    counts=ex.loc[ix].apply(pd.to_numeric,errors="coerce").fillna(0)+intr.loc[ix].apply(pd.to_numeric,errors="coerce").fillna(0)
    counts.columns=[str(c)[1:] if str(c).startswith("X") else str(c) for c in counts.columns]
    lib=counts.sum(axis=0).replace(0,np.nan)
    expr=np.log1p(counts.divide(lib,axis=1)*1e6)
    cellcol="cell id" if "cell id" in eph.columns else eph.columns[0]
    eph=eph.set_index(eph[cellcol].astype(str))
    cells=[c for c in expr.columns.astype(str) if c in eph.index]
    expr=expr[cells];eph=eph.loc[cells]
    available=[g for g in mouse_genes if g in expr.index]
    out={}
    for vf,mf in M1_MAP.items():
        if mf not in eph.columns:continue
        y=pd.to_numeric(eph[mf],errors="coerce").to_numpy(float)
        vals={}
        for g in available:
            x=pd.to_numeric(expr.loc[g],errors="coerce").to_numpy(float)
            ok=np.isfinite(x)&np.isfinite(y)
            if ok.sum()<100:continue
            r=spearmanr(x[ok],y[ok]).statistic
            vals[g]=float(r) if np.isfinite(r) else np.nan
        out[vf]=vals
    return out

def main():
    bio=pd.read_csv(BIO)
    cancer=pd.read_csv(CAN)
    # Keep a deterministic gene order from rank.
    meta=cancer[["rank","gene","mouse_gene"]].drop_duplicates().sort_values("rank")
    genes=meta["gene"].astype(str).tolist(); mouse=meta["mouse_gene"].astype(str).tolist()
    Edf=bio.pivot_table(index="gene",columns="feature",values="rho",aggfunc="first").reindex(genes)
    Cdf=cancer.pivot_table(index="gene",columns="study_id",values="mutation_percent",aggfunc="first").reindex(genes)
    if Edf.isna().any().any():raise RuntimeError("Missing entries in Top500 bioelectric matrix")
    if Cdf.isna().any().any():raise RuntimeError("Missing entries in Top500 cancer matrix")

    E=Edf.to_numpy(float)
    C=np.log1p(Cdf.to_numpy(float))
    Ez,_,_=zcols(E);Cz,_,_=zcols(C)
    rng=np.random.default_rng(20260921)

    ranks=[4,8,12]
    alphas=[0.0,0.25,1.0,4.0]
    reps=5;rows=[]
    for rep in range(reps):
        emask,etest=holdout_mask(Ez.shape,.10,rng)
        cmask,ctest=holdout_mask(Cz.shape,.10,rng)
        for k in ranks:
            # ephys-only baseline
            U,V,pred=als_factorize(Ez,emask,k=k,seed=1000+rep*100+k)
            rows.append({"rep":rep+1,"rank":k,"alpha":0.0,
                         "ephys_rmse":rmse(Ez[etest],pred[etest]),"cancer_rmse":None})
            for alpha in [x for x in alphas if x>0]:
                sa=np.sqrt(alpha)
                X=np.concatenate([Ez,Cz*sa],axis=1)
                mask=np.concatenate([emask,cmask],axis=1)
                U,V,pred=als_factorize(X,mask,k=k,seed=2000+rep*100+k+int(alpha*10))
                pe=pred[:,:Ez.shape[1]]
                pc=pred[:,Ez.shape[1]:]/sa
                rows.append({"rep":rep+1,"rank":k,"alpha":alpha,
                             "ephys_rmse":rmse(Ez[etest],pe[etest]),
                             "cancer_rmse":rmse(Cz[ctest],pc[ctest])})
    cv=pd.DataFrame(rows);cv.to_csv(DATA/"beam_factor_cv.csv",index=False)
    summ=cv.groupby(["rank","alpha"]).agg(
        mean_ephys_rmse=("ephys_rmse","mean"),sd_ephys_rmse=("ephys_rmse","std"),
        mean_cancer_rmse=("cancer_rmse","mean"),sd_cancer_rmse=("cancer_rmse","std")
    ).reset_index()
    # best joint model: lowest ephys RMSE among alpha>0, cancer RMSE finite
    joint=summ[summ.alpha>0].copy()
    best=joint.sort_values(["mean_ephys_rmse","mean_cancer_rmse"]).iloc[0]
    best_k=int(best["rank"]);best_alpha=float(best["alpha"])

    # Full reconstruction for external association-pattern test.
    _,_,pred_e=als_factorize(Ez,np.ones(Ez.shape,bool),k=best_k,seed=77)
    sa=np.sqrt(best_alpha)
    X=np.concatenate([Ez,Cz*sa],axis=1)
    _,_,pred_joint=als_factorize(X,np.ones(X.shape,bool),k=best_k,seed=78)
    pred_joint_e=pred_joint[:,:Ez.shape[1]]

    m1=load_m1_assoc(mouse)
    mouse_to_i={g:i for i,g in enumerate(mouse)}
    external=[]
    for trait,vals in m1.items():
        if trait not in Edf.columns:continue
        j=Edf.columns.get_loc(trait)
        pairs=[(mouse_to_i[g],r) for g,r in vals.items() if g in mouse_to_i and np.isfinite(r)]
        if len(pairs)<100:continue
        idx=np.array([x[0] for x in pairs],int);obs=np.array([x[1] for x in pairs],float)
        raw=E[idx,j]
        ep=pred_e[idx,j]
        jp=pred_joint_e[idx,j]
        def sp(x):
            r=spearmanr(x,obs).statistic
            return float(r) if np.isfinite(r) else None
        external.append({
          "trait":trait,"n_genes":len(idx),
          "raw_v1_vs_m1_spearman":sp(raw),
          "ephys_factor_vs_m1_spearman":sp(ep),
          "joint_factor_vs_m1_spearman":sp(jp)
        })
    ext=pd.DataFrame(external);ext.to_csv(DATA/"beam_factor_external_m1.csv",index=False)

    # embeddings and view loadings for portal/exploration
    U,V,recon=als_factorize(X,np.ones(X.shape,bool),k=best_k,seed=78)
    emb=pd.DataFrame(U,columns=[f"LF{i+1}" for i in range(best_k)])
    emb.insert(0,"mouse_gene",mouse);emb.insert(0,"gene",genes);emb.insert(0,"rank",meta["rank"].to_numpy())
    emb.to_csv(DATA/"beam_factor_gene_embeddings.csv",index=False)
    load=pd.DataFrame(V,columns=[f"LF{i+1}" for i in range(best_k)])
    load.insert(0,"node",list(Edf.columns)+list(Cdf.columns))
    load.insert(1,"view",["bioelectric"]*Edf.shape[1]+["cancer"]*Cdf.shape[1])
    load.to_csv(DATA/"beam_factor_view_loadings.csv",index=False)

    payload={
      "modelName":"BEAM-Factor",
      "objective":"shared-gene weighted multi-view matrix factorization",
      "genes":len(genes),"electricalTraits":Edf.shape[1],"cancerCohorts":Cdf.shape[1],
      "bestRank":best_k,"bestCancerWeight":best_alpha,
      "cv":summ.replace({np.nan:None}).to_dict(orient="records"),
      "externalM1":external,
      "externalSummary":{
        "rawMeanSpearman":float(ext["raw_v1_vs_m1_spearman"].mean()) if len(ext) else None,
        "ephysFactorMeanSpearman":float(ext["ephys_factor_vs_m1_spearman"].mean()) if len(ext) else None,
        "jointFactorMeanSpearman":float(ext["joint_factor_vs_m1_spearman"].mean()) if len(ext) else None
      },
      "guardrail":"Cancer view is an independent genomic context. Improved reconstruction or external reproducibility would support shared statistical structure, not causal cancer-to-neuron effects."
    }
    (DATA/"beam_factor_results.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    print(json.dumps({k:payload[k] for k in ["bestRank","bestCancerWeight","externalSummary"]},indent=2))

if __name__=="__main__":main()
