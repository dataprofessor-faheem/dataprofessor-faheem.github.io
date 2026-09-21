"""CBEF sensitivity, ablation and ranking-stability analysis."""
# Revalidated for NEURO-BEAM 3.0 release.
from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
FULL=DATA/"cbef_full_gene_catalog.csv"
CMAT=DATA/"cbef_full_cancer_matrix.csv"

def pct_rank(s):
    return pd.Series(s,dtype=float).rank(method="average",pct=True).fillna(0.0)

def jaccard(a,b):
    a,b=set(a),set(b)
    return len(a&b)/len(a|b) if a|b else np.nan

def rank_by(df,score):
    return df.sort_values([score,"best_abs_rho"],ascending=[False,False]).reset_index(drop=True)

def main():
    df=pd.read_csv(FULL)
    cm=pd.read_csv(CMAT)
    B=df.set_index("gene")["bioelectric_evidence_score"].astype(float)
    C=df.set_index("gene")["cancer_evidence_score"].astype(float)
    S=df.set_index("gene")["cross_domain_synergy"].astype(float)
    base=0.45*B+0.35*C+0.20*S
    genes=list(df["gene"])
    base_rank=base.sort_values(ascending=False)
    base_pos=pd.Series(np.arange(1,len(base_rank)+1),index=base_rank.index)

    # Deterministic ablations / alternative fusion rules.
    eps=1e-9
    alternatives={
      "bioelectric_only":B,
      "cancer_only":C,
      "equal_mean":0.5*B+0.5*C,
      "harmonic_mean":2*B*C/(B+C+eps),
      "synergy_only":S,
      "default_cbef":base
    }
    alt_rows=[]
    for name,score in alternatives.items():
        r=score.sort_values(ascending=False)
        pos=pd.Series(np.arange(1,len(r)+1),index=r.index)
        rho=spearmanr(base_pos.loc[genes],pos.loc[genes]).statistic
        alt_rows.append({
          "method":name,
          "rank_spearman_vs_default":float(rho),
          "top20_jaccard":jaccard(base_rank.head(20).index,r.head(20).index),
          "top50_jaccard":jaccard(base_rank.head(50).index,r.head(50).index),
          "top100_jaccard":jaccard(base_rank.head(100).index,r.head(100).index),
          "top500_jaccard":jaccard(base_rank.head(min(500,len(base_rank))).index,r.head(min(500,len(r))).index)
        })

    # Weight grid sensitivity with all three evidence terms.
    grid=[]
    for wb in np.arange(.20,.71,.05):
        for wc in np.arange(.20,.71,.05):
            ws=1-wb-wc
            if ws<.05 or ws>.40: continue
            score=wb*B+wc*C+ws*S
            r=score.sort_values(ascending=False)
            pos=pd.Series(np.arange(1,len(r)+1),index=r.index)
            rho=spearmanr(base_pos.loc[genes],pos.loc[genes]).statistic
            grid.append({
              "w_bioelectric":round(float(wb),2),"w_cancer":round(float(wc),2),"w_synergy":round(float(ws),2),
              "rank_spearman":float(rho),
              "top50_jaccard":jaccard(base_rank.head(50).index,r.head(50).index),
              "top100_jaccard":jaccard(base_rank.head(100).index,r.head(100).index),
              "top500_jaccard":jaccard(base_rank.head(min(500,len(r))).index,r.head(min(500,len(r))).index)
            })

    # Cohort bootstrap: recompute cancer evidence from resampled cancer cohorts.
    piv=cm.pivot_table(index="gene",columns="study_id",values="mutation_percent",aggfunc="first")
    piv=piv.reindex(index=genes)
    rng=np.random.default_rng(20260921)
    nboot=300
    sel20={g:0 for g in genes};sel50={g:0 for g in genes};sel100={g:0 for g in genes};sel500={g:0 for g in genes}
    boot_summary=[]
    studies=list(piv.columns)
    for b in range(nboot):
        sampled=rng.choice(studies,size=len(studies),replace=True)
        x=piv[sampled]
        mean=x.mean(axis=1,skipna=True)
        maxv=x.max(axis=1,skipna=True)
        breadth=(x.fillna(0)>0).sum(axis=1)
        Cr=(pct_rank(mean)+pct_rank(maxv)+pct_rank(breadth))/3.0
        Sr=np.sqrt(B.clip(0,1)*Cr.clip(0,1))
        score=.45*B+.35*Cr+.20*Sr
        r=score.sort_values(ascending=False)
        for g in r.head(20).index:sel20[g]+=1
        for g in r.head(50).index:sel50[g]+=1
        for g in r.head(100).index:sel100[g]+=1
        for g in r.head(min(500,len(r))).index:sel500[g]+=1
        boot_summary.append({
          "bootstrap":b+1,
          "top50_jaccard":jaccard(base_rank.head(50).index,r.head(50).index),
          "top100_jaccard":jaccard(base_rank.head(100).index,r.head(100).index),
          "top500_jaccard":jaccard(base_rank.head(min(500,len(r))).index,r.head(min(500,len(r))).index)
        })

    stability=pd.DataFrame({
      "gene":genes,
      "base_rank":[int(base_pos[g]) for g in genes],
      "top20_selection_frequency":[sel20[g]/nboot for g in genes],
      "top50_selection_frequency":[sel50[g]/nboot for g in genes],
      "top100_selection_frequency":[sel100[g]/nboot for g in genes],
      "top500_selection_frequency":[sel500[g]/nboot for g in genes]
    }).sort_values("base_rank")
    stability.to_csv(DATA/"cbef_bootstrap_gene_stability.csv",index=False)
    pd.DataFrame(grid).to_csv(DATA/"cbef_weight_sensitivity.csv",index=False)
    pd.DataFrame(alt_rows).to_csv(DATA/"cbef_fusion_ablations.csv",index=False)
    pd.DataFrame(boot_summary).to_csv(DATA/"cbef_cohort_bootstrap.csv",index=False)

    # Cross-domain negative control: permute cancer evidence across genes.
    null=[]
    base_top50_mean=float(base.loc[base_rank.head(50).index].mean())
    for i in range(1000):
        Cp=pd.Series(rng.permutation(C.to_numpy()),index=C.index)
        Sp=np.sqrt(B.clip(0,1)*Cp.clip(0,1))
        score=.45*B+.35*Cp+.20*Sp
        null.append(float(score.nlargest(50).mean()))
    null=np.asarray(null)
    empirical_p=float((1+np.sum(null>=base_top50_mean))/(len(null)+1))
    np.savetxt(DATA/"cbef_permutation_null_top50.csv",null,delimiter=",",header="top50_mean_score",comments="")

    summary={
      "nGenes":len(df),"nCohorts":len(studies),"bootstrapIterations":nboot,"permutationIterations":len(null),
      "ablations":alt_rows,
      "weightSensitivity":{
        "medianRankSpearman":float(pd.DataFrame(grid)["rank_spearman"].median()),
        "minRankSpearman":float(pd.DataFrame(grid)["rank_spearman"].min()),
        "medianTop50Jaccard":float(pd.DataFrame(grid)["top50_jaccard"].median()),
        "minTop50Jaccard":float(pd.DataFrame(grid)["top50_jaccard"].min())
      },
      "cohortBootstrap":{
        "meanTop50Jaccard":float(pd.DataFrame(boot_summary)["top50_jaccard"].mean()),
        "meanTop100Jaccard":float(pd.DataFrame(boot_summary)["top100_jaccard"].mean()),
        "meanTop500Jaccard":float(pd.DataFrame(boot_summary)["top500_jaccard"].mean())
      },
      "permutationNegativeControl":{
        "observedTop50MeanScore":base_top50_mean,
        "nullMean":float(null.mean()),"null95":float(np.quantile(null,.95)),
        "empiricalP":empirical_p
      },
      "topStableGenes":stability.head(50).to_dict(orient="records")
    }
    (DATA/"cbef_sensitivity_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps({k:summary[k] for k in ["nGenes","nCohorts","weightSensitivity","cohortBootstrap","permutationNegativeControl"]},indent=2))

if __name__=="__main__":main()
