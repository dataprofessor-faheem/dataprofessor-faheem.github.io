"""Multi-objective Pareto ranking and evidence tiers for NEURO-BEAM 3.0."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/"data"
CAT=DATA/"cbef_full_gene_catalog.csv"
STAB=DATA/"cbef_bootstrap_gene_stability.csv"
IMP=DATA/"ml_extratrees_global_feature_importance.csv"
EXT=DATA/"gene_external_m1_replication_summary.csv"

def pct(s):
    return pd.Series(s,dtype=float).rank(method="average",pct=True).fillna(0.0)

def pareto_fronts(X):
    # Higher is better in every column. Iterative nondominated sorting.
    X=np.asarray(X,float);n=len(X);remaining=set(range(n));front=np.full(n,-1,int);level=1
    while remaining:
        idx=list(remaining);vals=X[idx]
        nondom=[]
        for a,i in enumerate(idx):
            dominated=False
            for b,j in enumerate(idx):
                if i==j:continue
                if np.all(vals[b]>=vals[a]) and np.any(vals[b]>vals[a]):
                    dominated=True;break
            if not dominated:nondom.append(i)
        if not nondom:
            for i in remaining:front[i]=level
            break
        for i in nondom:
            front[i]=level;remaining.remove(i)
        level+=1
    return front

def main():
    cat=pd.read_csv(CAT)
    stab=pd.read_csv(STAB) if STAB.exists() else pd.DataFrame()
    imp=pd.read_csv(IMP)
    imp["importance_percentile"]=pct(imp.importance)
    imp=imp.rename(columns={"gene":"mouse_gene"})[["mouse_gene","importance","importance_percentile"]]

    x=cat.merge(imp,on="mouse_gene",how="left")
    if len(stab):
        x=x.merge(stab[["gene","top20_selection_frequency","top50_selection_frequency","top100_selection_frequency","top500_selection_frequency"]],on="gene",how="left")
    else:
        for c in ["top20_selection_frequency","top50_selection_frequency","top100_selection_frequency","top500_selection_frequency"]:x[c]=np.nan

    if EXT.exists():
        ext=pd.read_csv(EXT)
        x=x.merge(ext[["gene","sign_concordance_fraction","mean_geometric_abs_strength","trait_fingerprint_spearman","external_replication_score"]],on="gene",how="left")
    else:
        for c in ["sign_concordance_fraction","mean_geometric_abs_strength","trait_fingerprint_spearman","external_replication_score"]:x[c]=np.nan

    x["importance"]=x.importance.fillna(0);x["importance_percentile"]=x.importance_percentile.fillna(0)
    x["external_replication_score"]=x.external_replication_score.fillna(0)
    x["top100_selection_frequency"]=x.top100_selection_frequency.fillna(0)

    # Five independent objectives; no weighted sum determines Pareto membership.
    cols=["bioelectric_evidence_score","cancer_evidence_score","top100_selection_frequency","importance_percentile","external_replication_score"]
    X=x[cols].fillna(0).to_numpy(float)
    x["pareto_front"]=pareto_fronts(X)

    # Descriptive consensus percentile only; not used to define the Pareto front.
    x["consensus_evidence_percentile"]=[
        float(np.mean(row)) for row in X
    ]

    # Pre-specified evidence tiers.
    A=(x.bioelectric_evidence_score>=.75)&(x.cancer_evidence_score>=.50)&(x.top100_selection_frequency>=.90)&(x.importance_percentile>=.70)&(x.external_replication_score>=.60)
    B=(~A)&(x.bioelectric_evidence_score>=.65)&(x.top100_selection_frequency>=.80)&((x.importance_percentile>=.60)|(x.external_replication_score>=.40))
    C=(~A)&(~B)&(x["rank"]<=500)
    x["evidence_tier"]=np.select([A,B,C],["A — replicated","B — robust","C — exploratory"],default="Outside Top-500")

    # Independent flags.
    x["external_replication_flag"]=np.where(x.external_replication_score>=.60,"strong",np.where(x.external_replication_score>=.40,"moderate","limited"))
    x["stability_flag"]=np.where(x.top100_selection_frequency>=.90,"high",np.where(x.top100_selection_frequency>=.70,"moderate","low"))
    x["predictive_importance_flag"]=np.where(x.importance_percentile>=.80,"high",np.where(x.importance_percentile>=.50,"moderate","low"))

    # Research-facing rank: Pareto front first, then consensus percentile. This is not a learned risk score.
    x=x.sort_values(["pareto_front","consensus_evidence_percentile","cbef_discovery_score"],ascending=[True,False,False]).reset_index(drop=True)
    x["pareto_rank"]=np.arange(1,len(x)+1)
    x.to_csv(DATA/"neurobeam_pareto_evidence_catalog.csv",index=False)
    x[x["rank"]<=500].to_csv(DATA/"top500_evidence_tiers.csv",index=False)

    payload={
      "objectives":cols,
      "tierDefinitions":{
        "A":"bioelectric>=0.75; cancer>=0.50; Top100 bootstrap frequency>=0.90; predictive-importance percentile>=0.70; external replication>=0.60",
        "B":"bioelectric>=0.65; Top100 bootstrap frequency>=0.80; predictive importance>=0.60 OR external replication>=0.40",
        "C":"current Top-500 without A/B criteria"
      },
      "counts":x.evidence_tier.value_counts().to_dict(),
      "paretoFrontCounts":x.pareto_front.value_counts().sort_index().to_dict(),
      "top500":x[x["rank"]<=500].head(500).replace({np.nan:None}).to_dict(orient="records"),
      "guardrail":"Pareto fronts are multi-objective prioritization, not causal or clinical rankings. Evidence tiers require independent stability/replication criteria."
    }
    (DATA/"neurobeam_pareto_evidence.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    print(json.dumps({"counts":payload["counts"],"fronts":list(payload["paretoFrontCounts"].items())[:6],"top":x.head(12)[["gene","pareto_front","evidence_tier","external_replication_score","top100_selection_frequency","importance_percentile"]].to_dict(orient="records")},indent=2))

if __name__=="__main__":main()
