"""Build NEURO-BEAM Top-500 cancer–bioelectric discovery panel.

Data:
- 1,302 genes from same-cell visual-cortex Patch-seq association analysis
- 10 TCGA PanCancer Atlas cohorts from existing cBioPortal catalog

Cancer evidence:
- mutation prevalence per cohort, using mutation-sequenced sample-list denominator
- mean prevalence, maximum prevalence, fraction of cohorts with >=1 mutated sample

Bioelectric evidence:
- maximum |Spearman rho| across 18 electrical traits
- fraction of traits with BH-FDR q < 0.05

Composite Discovery Priority Score:
- CancerScore = mean percentile(mean prevalence, max prevalence, cohort recurrence)
- BioelectricScore = mean percentile(max |rho|, significant-trait fraction)
- DPS = 0.5 * CancerScore + 0.5 * BioelectricScore

This is a transparent prioritization index, not a causal/clinical score.
"""
from __future__ import annotations
import json,time,math
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"; DATA.mkdir(parents=True,exist_ok=True)
ASSOC=DATA/"bioelectric_gene_associations.csv"
DIS=DATA/"disease_bioelectric_bridge.json"
BASE="https://www.cbioportal.org/api"
MYGENE="https://mygene.info/v3"

S=requests.Session()
S.headers.update({"accept":"application/json","User-Agent":"NEURO-BEAM-Top500/1.0"})

def percentile(series):
    return pd.Series(series).rank(method="average",pct=True).to_numpy(float)

def human_entrez(symbol):
    # Mouse symbols are generally title case; try uppercase human orthographic equivalent.
    hs=str(symbol).upper()
    r=S.get(MYGENE+"/query",params={"q":f"symbol:{hs}","species":"human","fields":"symbol,entrezgene","size":5},timeout=60)
    r.raise_for_status()
    hits=r.json().get("hits",[])
    exact=[h for h in hits if str(h.get("symbol","")).upper()==hs and h.get("entrezgene")]
    if exact:return hs,int(exact[0]["entrezgene"])
    return None,None

def post_mutations(profile,sample_list,entrez_ids):
    url=f"{BASE}/molecular-profiles/{profile}/mutations/fetch"
    body={"sampleListId":sample_list,"entrezGeneIds":[int(x) for x in entrez_ids]}
    r=S.post(url,params={"projection":"DETAILED"},json=body,timeout=240)
    r.raise_for_status()
    return r.json()

def main():
    assoc=pd.read_csv(ASSOC)
    dis=json.loads(DIS.read_text(encoding="utf-8"))
    studies=dis["studies"]

    # All Patch-seq genes and bioelectric summaries.
    genes=sorted(assoc["gene"].dropna().astype(str).unique())
    mapping=[]
    for i,g in enumerate(genes):
        try:
            hs,eid=human_entrez(g)
        except Exception:
            hs,eid=None,None
        mapping.append({"mouse_gene":g,"gene":hs,"entrez_id":eid})
        if (i+1)%100==0: print("mapped",i+1,"/",len(genes))
        time.sleep(.01)
    mp=pd.DataFrame(mapping)
    mp.to_csv(DATA/"top500_mouse_human_gene_map.csv",index=False)
    valid=mp.dropna(subset=["entrez_id","gene"]).copy()
    valid["entrez_id"]=valid["entrez_id"].astype(int)
    eid_to_gene=dict(zip(valid.entrez_id,valid.gene))
    human_to_mouse=dict(zip(valid.gene,valid.mouse_gene))

    # Bioelectric metrics.
    bio=[]
    for hs,mg in human_to_mouse.items():
        a=assoc[assoc.gene.astype(str)==mg]
        if a.empty:continue
        max_abs=float(a.rho.abs().max())
        best=a.loc[a.rho.abs().idxmax()]
        sigfrac=float((a.q<=0.05).mean())
        bio.append({
            "gene":hs,"mouse_gene":mg,
            "max_abs_rho":max_abs,
            "best_feature":str(best.feature),
            "best_rho":float(best.rho),
            "best_q":float(best.q) if pd.notna(best.q) else None,
            "significant_trait_fraction":sigfrac,
            "significant_trait_count":int((a.q<=0.05).sum()),
            "n_traits_tested":int(len(a)),
            "matched_neuron_n":int(best.n)
        })
    bio=pd.DataFrame(bio)

    # Cancer mutation prevalence per study. Batch genes to keep requests manageable.
    mut_counts=defaultdict(lambda:defaultdict(set))
    cancer_rows=[]
    batch_size=400
    valid_ids=valid.entrez_id.tolist()
    for s in studies:
        sid=s["studyId"]; profile=s["mutationProfileId"]
        # Use the same mutation-sequenced sample list used as denominator.
        sample_list=s["sampleListId"]
        denom=int(s["mutationSequencedDenominator"])
        for j in range(0,len(valid_ids),batch_size):
            batch=valid_ids[j:j+batch_size]
            try:
                muts=post_mutations(profile,sample_list,batch)
            except Exception as e:
                print("batch error",sid,j,repr(e))
                # fallback through _all list and filter against denominator list is not available here;
                # fail batch as NA later rather than zero.
                continue
            for m in muts:
                eid=(m.get("gene") or {}).get("entrezGeneId") or m.get("entrezGeneId")
                samp=str(m.get("sampleId") or "")
                if eid is not None and samp:
                    mut_counts[sid][int(eid)].add(samp)
            time.sleep(.05)

        for _,r in valid.iterrows():
            eid=int(r.entrez_id); g=r.gene
            n=len(mut_counts[sid].get(eid,set()))
            cancer_rows.append({
                "study_id":sid,"study_name":s["name"],"cancer_type":s["cancerTypeName"],
                "mutation_sequenced_n":denom,"gene":g,"mouse_gene":r.mouse_gene,
                "entrez_id":eid,"mutated_samples":n,
                "mutation_percent":(100*n/denom) if denom else None
            })
        print("study complete",sid)

    cancer=pd.DataFrame(cancer_rows)
    cancer.to_csv(DATA/"top500_all_gene_cancer_matrix.csv",index=False)

    # Summary per gene.
    cs=[]
    for g,x in cancer.groupby("gene"):
        vals=x.mutation_percent.dropna()
        if vals.empty:continue
        cs.append({
            "gene":g,
            "mean_mutation_percent":float(vals.mean()),
            "max_mutation_percent":float(vals.max()),
            "cohort_recurrence_fraction":float((x.mutated_samples>0).mean()),
            "cohorts_with_mutation":int((x.mutated_samples>0).sum())
        })
    cs=pd.DataFrame(cs)

    merged=bio.merge(cs,on="gene",how="inner")
    if merged.empty: raise RuntimeError("No human-mapped genes with cancer + bioelectric evidence")

    # Transparent percentile-based component scores.
    merged["cancer_mean_pctile"]=percentile(merged.mean_mutation_percent)
    merged["cancer_max_pctile"]=percentile(merged.max_mutation_percent)
    merged["cancer_recurrence_pctile"]=percentile(merged.cohort_recurrence_fraction)
    merged["cancer_score"]=(merged.cancer_mean_pctile+merged.cancer_max_pctile+merged.cancer_recurrence_pctile)/3

    merged["bio_rho_pctile"]=percentile(merged.max_abs_rho)
    merged["bio_sigtrait_pctile"]=percentile(merged.significant_trait_fraction)
    merged["bioelectric_score"]=(merged.bio_rho_pctile+merged.bio_sigtrait_pctile)/2
    merged["discovery_priority_score"]=0.5*merged.cancer_score+0.5*merged.bioelectric_score

    merged=merged.sort_values(["discovery_priority_score","max_abs_rho","mean_mutation_percent"],ascending=False).reset_index(drop=True)
    merged["rank"]=np.arange(1,len(merged)+1)
    top=merged.head(500).copy()
    top.to_csv(DATA/"top500_cancer_bioelectric_genes.csv",index=False)

    topgenes=set(top.gene)
    cancer[cancer.gene.isin(topgenes)].to_csv(DATA/"top500_cancer_matrix.csv",index=False)

    # All gene x signal associations for top500.
    amap=dict(zip(valid.mouse_gene,valid.gene))
    aa=assoc.copy()
    aa["gene_human"]=aa.gene.map(amap)
    aa=aa[aa.gene_human.isin(topgenes)].copy()
    aa=aa.rename(columns={"gene":"mouse_gene","gene_human":"gene"})
    aa.to_csv(DATA/"top500_bioelectric_matrix.csv",index=False)

    payload={
        "method":{
            "cancerScore":"mean of percentiles: mean mutation prevalence, max mutation prevalence, cohort recurrence",
            "bioelectricScore":"mean of percentiles: max absolute Spearman rho, fraction of 18 traits with BH-FDR q<0.05",
            "discoveryPriorityScore":"0.5 × CancerScore + 0.5 × BioelectricScore",
            "interpretation":"prioritization only; not causal or clinical"
        },
        "nPatchseqGenes":len(genes),
        "nHumanMappedGenes":int(len(valid)),
        "nRankedGenes":int(len(merged)),
        "top500":top.replace({np.nan:None}).to_dict(orient="records"),
        "studies":[{"studyId":s["studyId"],"name":s["name"],"cancerTypeName":s["cancerTypeName"],"n":s["mutationSequencedDenominator"]} for s in studies],
        "electricalFeatures":sorted(aa.feature.unique().tolist()),
        "downloads":{
            "catalog":"data/top500_cancer_bioelectric_genes.csv",
            "cancerMatrix":"data/top500_cancer_matrix.csv",
            "bioelectricMatrix":"data/top500_bioelectric_matrix.csv",
            "geneMap":"data/top500_mouse_human_gene_map.csv"
        }
    }
    (DATA/"top500_cancer_bioelectric_genes.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    print(json.dumps({"patchseqGenes":len(genes),"humanMapped":len(valid),"ranked":len(merged),"top500":len(top),"top10":top[["rank","gene","discovery_priority_score","best_feature","best_rho","mean_mutation_percent"]].head(10).to_dict(orient="records")},indent=2))

if __name__=="__main__": main()
