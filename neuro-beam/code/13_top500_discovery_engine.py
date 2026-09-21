"""NEURO-BEAM CBEF Top-500 Discovery Engine.

Builds a cross-domain gene ranking from:
1) same-cell neuronal transcriptome–electrophysiology associations; and
2) mutation prevalence across 10 cBioPortal cancer cohorts.

The ranking is evidence fusion, not causal inference.
"""
from __future__ import annotations
import json, math, time
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
ASSOC=DATA/"bioelectric_gene_associations.csv"
DISEASE=DATA/"disease_bioelectric_bridge.json"
BASE="https://www.cbioportal.org/api"
MYGENE="https://mygene.info/v3"

S=requests.Session()
S.headers.update({"accept":"application/json","User-Agent":"NEURO-BEAM-CBEF/1.0"})

def pct_rank(s):
    s=pd.Series(s,dtype=float)
    return s.rank(method="average",pct=True).fillna(0.0)

def resolve_human_ortholog(mouse_symbol):
    # First resolve mouse gene and homologene human ortholog.
    try:
        r=S.get(MYGENE+"/query",params={
            "q":f"symbol:{mouse_symbol}",
            "species":"mouse",
            "fields":"symbol,entrezgene,homologene",
            "size":5
        },timeout=40)
        r.raise_for_status()
        hits=r.json().get("hits",[])
        exact=[h for h in hits if str(h.get("symbol","")).lower()==str(mouse_symbol).lower()]
        if exact:
            h=exact[0]
            hg=h.get("homologene")
            genes=(hg or {}).get("genes",[]) if isinstance(hg,dict) else []
            for tax,gid in genes:
                if int(tax)==9606:
                    rr=S.get(MYGENE+"/gene/"+str(gid),params={"fields":"symbol,entrezgene"},timeout=30)
                    if rr.ok:
                        j=rr.json()
                        if j.get("symbol") and j.get("entrezgene"):
                            return str(j["symbol"]).upper(),int(j["entrezgene"]),"homologene"
    except Exception:
        pass
    # Conservative same-symbol fallback.
    try:
        hs=str(mouse_symbol).upper()
        r=S.get(MYGENE+"/query",params={
            "q":f"symbol:{hs}",
            "species":"human",
            "fields":"symbol,entrezgene",
            "size":5
        },timeout=40)
        r.raise_for_status()
        hits=r.json().get("hits",[])
        exact=[h for h in hits if str(h.get("symbol","")).upper()==hs and h.get("entrezgene")]
        if exact:
            return str(exact[0]["symbol"]).upper(),int(exact[0]["entrezgene"]),"same-symbol"
    except Exception:
        pass
    return None,None,None

def get_sample_ids(sample_list_id):
    r=S.get(BASE+f"/sample-lists/{sample_list_id}",params={"projection":"DETAILED"},timeout=60)
    r.raise_for_status()
    return [str(x) for x in (r.json().get("sampleIds") or [])]

def fetch_mutations_batch(profile_id, entrez_ids, sample_ids):
    # Preferred current POST endpoint for a single molecular profile.
    url=BASE+f"/molecular-profiles/{profile_id}/mutations/fetch"
    body={"entrezGeneIds":[int(x) for x in entrez_ids],"sampleIds":[str(x) for x in sample_ids]}
    r=S.post(url,params={"projection":"DETAILED"},json=body,timeout=180)
    if r.ok:
        return r.json()
    # Fallback multi-profile endpoint used by current clients.
    url2=BASE+"/mutations/fetch"
    body2={"entrezGeneIds":[int(x) for x in entrez_ids],"molecularProfileIds":[profile_id],"sampleIds":[str(x) for x in sample_ids]}
    r2=S.post(url2,params={"projection":"DETAILED"},json=body2,timeout=180)
    r2.raise_for_status()
    return r2.json()

def main():
    assoc=pd.read_csv(ASSOC)
    assoc["abs_rho"]=assoc["rho"].abs()
    gstats=assoc.groupby("gene").agg(
        best_abs_rho=("abs_rho","max"),
        min_q=("q","min"),
        sig_trait_count=("q",lambda x:int((pd.to_numeric(x,errors="coerce")<=0.05).sum())),
        mean_abs_rho=("abs_rho","mean"),
        matched_neuron_n=("n","max")
    ).reset_index()
    best_idx=assoc.groupby("gene")["abs_rho"].idxmax()
    best=assoc.loc[best_idx,["gene","feature","rho","q"]].rename(columns={
        "feature":"best_electrical_feature","rho":"best_rho","q":"best_feature_q"
    })
    gstats=gstats.merge(best,on="gene",how="left")
    gstats["neglog10q"]=-np.log10(pd.to_numeric(gstats["min_q"],errors="coerce").clip(lower=1e-300))

    # Map the complete neuronal gene universe to human orthologs.
    maps=[]
    for i,g in enumerate(gstats["gene"].astype(str)):
        hs,eid,method=resolve_human_ortholog(g)
        maps.append({"mouse_gene":g,"gene":hs,"entrez_id":eid,"ortholog_method":method})
        if (i+1)%100==0: print("orthologs",i+1,"/",len(gstats),flush=True)
        time.sleep(0.015)
    mapping=pd.DataFrame(maps)
    mapped=gstats.merge(mapping,left_on="gene",right_on="mouse_gene",how="left",suffixes=("_mouse",""))
    mapped=mapped[mapped["gene"].notna() & mapped["entrez_id"].notna()].copy()
    mapped["entrez_id"]=mapped["entrez_id"].astype(int)
    # If several mouse genes resolve to the same human symbol retain the strongest electrical evidence.
    mapped=mapped.sort_values(["gene","best_abs_rho"],ascending=[True,False]).drop_duplicates("gene",keep="first")

    disease=json.loads(DISEASE.read_text(encoding="utf-8"))
    studies=disease.get("studies",[])
    ids=mapped["entrez_id"].astype(int).tolist()
    eid_to_gene=dict(zip(mapped["entrez_id"].astype(int),mapped["gene"]))

    mut_by_gene_study={g:{} for g in mapped["gene"]}
    event_by_gene_study={g:{} for g in mapped["gene"]}
    study_meta=[]
    errors=[]

    for s in studies:
        sid=s["studyId"]
        prof=s.get("mutationProfileId") or sid+"_mutations"
        list_id=s.get("sampleListId") or sid+"_sequenced"
        try:
            sample_ids=get_sample_ids(list_id)
        except Exception:
            sample_ids=[]
        denom=len(set(sample_ids)) or int(s.get("mutationSequencedDenominator") or s.get("catalogSampleCount") or 0)
        altered=defaultdict(set); events=defaultdict(int)
        try:
            for start in range(0,len(ids),250):
                chunk=ids[start:start+250]
                rows=fetch_mutations_batch(prof,chunk,sample_ids)
                for m in rows:
                    eid=(m.get("gene") or {}).get("entrezGeneId") or m.get("entrezGeneId")
                    try:eid=int(eid)
                    except:continue
                    gene=eid_to_gene.get(eid)
                    if not gene: continue
                    sample=str(m.get("sampleId") or "")
                    if sample: altered[gene].add(sample)
                    events[gene]+=1
                time.sleep(0.1)
        except Exception as e:
            errors.append({"studyId":sid,"error":repr(e),"profile":prof,"sampleListId":list_id})
        for g in mapped["gene"]:
            if any(x.get("studyId")==sid for x in errors):
                mut_by_gene_study[g][sid]=None
                event_by_gene_study[g][sid]=None
            else:
                n=len(altered[g])
                mut_by_gene_study[g][sid]=(100*n/denom) if denom else None
                event_by_gene_study[g][sid]=events[g]
        study_meta.append({
            "studyId":sid,"name":s.get("name",sid),"cancerTypeName":s.get("cancerTypeName",""),
            "denominator":denom,"sampleListId":list_id,"mutationProfileId":prof
        })
        print("completed",sid,"n=",denom,flush=True)

    # Cancer evidence summary.
    crows=[]
    for g in mapped["gene"]:
        vals=[v for v in mut_by_gene_study[g].values() if v is not None]
        crows.append({
            "gene":g,
            "mean_mutation_percent":float(np.mean(vals)) if vals else np.nan,
            "max_mutation_percent":float(np.max(vals)) if vals else np.nan,
            "median_mutation_percent":float(np.median(vals)) if vals else np.nan,
            "cancer_cohort_breadth":int(sum(1 for v in vals if v>0)),
            "cancer_cohort_gt1pct":int(sum(1 for v in vals if v>=1.0))
        })
    cancer=pd.DataFrame(crows)
    df=mapped.merge(cancer,on="gene",how="left")

    # CBEF rank fusion uses percentile-normalized evidence to avoid arbitrary scale dominance.
    df["bio_rho_pct"]=pct_rank(df["best_abs_rho"])
    df["bio_sig_pct"]=pct_rank(df["sig_trait_count"])
    df["bio_q_pct"]=pct_rank(df["neglog10q"])
    df["bioelectric_evidence_score"]=(df["bio_rho_pct"]+df["bio_sig_pct"]+df["bio_q_pct"])/3.0

    df["cancer_mean_pct_rank"]=pct_rank(df["mean_mutation_percent"])
    df["cancer_max_pct_rank"]=pct_rank(df["max_mutation_percent"])
    df["cancer_breadth_pct_rank"]=pct_rank(df["cancer_cohort_breadth"])
    df["cancer_evidence_score"]=(df["cancer_mean_pct_rank"]+df["cancer_max_pct_rank"]+df["cancer_breadth_pct_rank"])/3.0

    df["cross_domain_synergy"]=np.sqrt(df["bioelectric_evidence_score"].clip(0,1)*df["cancer_evidence_score"].clip(0,1))
    df["cbef_discovery_score"]=0.45*df["bioelectric_evidence_score"]+0.35*df["cancer_evidence_score"]+0.20*df["cross_domain_synergy"]

    df=df.sort_values(["cbef_discovery_score","best_abs_rho"],ascending=False).reset_index(drop=True)
    df["rank"]=np.arange(1,len(df)+1)
    top=df.head(min(500,len(df))).copy()

    top_cols=[
        "rank","gene","mouse_gene","entrez_id","ortholog_method",
        "cbef_discovery_score","bioelectric_evidence_score","cancer_evidence_score","cross_domain_synergy",
        "best_electrical_feature","best_rho","best_feature_q","best_abs_rho","sig_trait_count","mean_abs_rho",
        "matched_neuron_n","mean_mutation_percent","median_mutation_percent","max_mutation_percent",
        "cancer_cohort_breadth","cancer_cohort_gt1pct"
    ]
    top[top_cols].to_csv(DATA/"top500_gene_catalog.csv",index=False)
    df[top_cols].to_csv(DATA/"cbef_full_gene_catalog.csv",index=False)

    # Long cancer and bioelectric matrices for downstream work.
    cancer_long=[]
    for _,r in top.iterrows():
        g=r["gene"]
        for s in study_meta:
            sid=s["studyId"]
            cancer_long.append({
                "rank":int(r["rank"]),"gene":g,"mouse_gene":r["mouse_gene"],"study_id":sid,
                "study_name":s["name"],"cancer_type":s["cancerTypeName"],"mutation_sequenced_n":s["denominator"],
                "mutation_percent":mut_by_gene_study[g].get(sid),"mutation_events":event_by_gene_study[g].get(sid),
                "cbef_discovery_score":r["cbef_discovery_score"]
            })
    pd.DataFrame(cancer_long).to_csv(DATA/"top500_cancer_matrix.csv",index=False)

    full_cancer_long=[]
    for _,r in df.iterrows():
        g=r["gene"]
        for sm in study_meta:
            sid=sm["studyId"]
            full_cancer_long.append({
                "rank":int(r["rank"]),"gene":g,"mouse_gene":r["mouse_gene"],"study_id":sid,
                "study_name":sm["name"],"cancer_type":sm["cancerTypeName"],"mutation_sequenced_n":sm["denominator"],
                "mutation_percent":mut_by_gene_study[g].get(sid),"mutation_events":event_by_gene_study[g].get(sid),
                "bioelectric_evidence_score":r["bioelectric_evidence_score"],
                "cancer_evidence_score":r["cancer_evidence_score"],
                "cbef_discovery_score":r["cbef_discovery_score"]
            })
    pd.DataFrame(full_cancer_long).to_csv(DATA/"cbef_full_cancer_matrix.csv",index=False)

    top_mouse=set(top["mouse_gene"].astype(str))
    bio_long=assoc[assoc["gene"].astype(str).isin(top_mouse)].copy()
    reverse=dict(zip(top["mouse_gene"],top["gene"]))
    ranks=dict(zip(top["gene"],top["rank"]))
    bio_long["human_gene"]=bio_long["gene"].map(reverse)
    bio_long["rank"]=bio_long["human_gene"].map(ranks)
    bio_long.rename(columns={"gene":"mouse_gene","human_gene":"gene"},inplace=True)
    bio_long.to_csv(DATA/"top500_bioelectric_matrix.csv",index=False)

    # Compact browser JSON.
    by_mouse={g:grp.sort_values("abs_rho",ascending=False).to_dict(orient="records")
              for g,grp in assoc[assoc["gene"].astype(str).isin(top_mouse)].groupby("gene")}
    payload={
        "method":"CBEF v1.0",
        "methodName":"Cross-Domain Bioelectric Evidence Fusion",
        "nMappedGenes":int(len(df)),
        "nRankedGenes":int(len(top)),
        "studies":study_meta,
        "errors":errors,
        "genes":[]
    }
    for _,r in top.iterrows():
        g=r["gene"]; mg=r["mouse_gene"]
        payload["genes"].append({
            "rank":int(r["rank"]),"gene":g,"mouseGene":mg,"entrezId":int(r["entrez_id"]),
            "orthologMethod":r["ortholog_method"],
            "discoveryScore":float(r["cbef_discovery_score"]),
            "bioelectricEvidenceScore":float(r["bioelectric_evidence_score"]),
            "cancerEvidenceScore":float(r["cancer_evidence_score"]),
            "crossDomainSynergy":float(r["cross_domain_synergy"]),
            "bestElectricalFeature":r["best_electrical_feature"],
            "bestRho":float(r["best_rho"]),"bestQ":float(r["best_feature_q"]),
            "significantTraitCount":int(r["sig_trait_count"]),
            "meanMutationPercent":None if pd.isna(r["mean_mutation_percent"]) else float(r["mean_mutation_percent"]),
            "maxMutationPercent":None if pd.isna(r["max_mutation_percent"]) else float(r["max_mutation_percent"]),
            "cohortBreadth":int(r["cancer_cohort_breadth"]),
            "mutations":mut_by_gene_study[g],
            "electricalAssociations":[
                {"feature":x["feature"],"rho":x["rho"],"p":x["p"],"q":x["q"],"n":x["n"]}
                for x in by_mouse.get(mg,[])
            ]
        })
    (DATA/"top500_discovery_catalog.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    print(json.dumps({
        "mapped":len(df),"top":len(top),"errors":errors[:3],
        "leaders":[{"rank":int(r["rank"]),"gene":r["gene"],"score":round(float(r["cbef_discovery_score"]),4)}
                   for _,r in top.head(15).iterrows()]
    },indent=2))

if __name__=="__main__": main()
