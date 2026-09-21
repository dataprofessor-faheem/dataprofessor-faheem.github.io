"""NEURO-BEAM Advanced Disease Genomics Bridge.

Builds a researcher-facing, reproducible cross-study mutation analysis across
the 10 default cBioPortal cohorts.

IMPORTANT:
- This is an exploratory disease-genomics layer.
- It is NOT the frozen neuronal Bioelectric Gene Signature.
- Denominators use mutation-sequenced sample lists where available.
- Output is JSON + CSV for browser visualization and downstream research reuse.
"""
from __future__ import annotations
import json, time, math
from pathlib import Path
from collections import defaultdict
import requests
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"; DATA.mkdir(parents=True,exist_ok=True)
CATALOG=DATA/"cbioportal_study_catalog.json"
BASE="https://www.cbioportal.org/api"

MODULES={
  "Ion channels / membrane excitability":[
    "SCN1A","SCN2A","SCN8A","KCNQ2","KCNQ3","KCNA1","KCNC1","HCN1","CACNA1C","CACNA1A","CLCN2","ATP1A3"
  ],
  "Activity / calcium signaling":[
    "NPAS4","ARC","FOS","EGR1","BDNF","CAMK2A","CREB1","PPP3CA"
  ],
  "DNA damage / chromatin":[
    "ATM","ATR","H2AFX","PARP1","BRCA1","BRCA2","TOP2B","TP53"
  ],
  "PI3K-MAPK-mTOR / cancer signaling":[
    "EGFR","PTEN","PIK3CA","KRAS","BRAF","AKT1","MTOR"
  ],
  "Oxidative / mitochondrial stress":[
    "NFE2L2","KEAP1","SOD2","GPX4","TFAM","PPARGC1A"
  ]
}
GENES=sorted({g for gs in MODULES.values() for g in gs})

S=requests.Session()
S.headers.update({"accept":"application/json","User-Agent":"NEURO-BEAM/2.0"})

def get(path,params=None,allow404=False):
    r=S.get(BASE+path,params=params,timeout=120)
    if allow404 and r.status_code==404: return None
    r.raise_for_status()
    return r.json()

def mutation_profile(study):
    profs=get(f"/studies/{study}/molecular-profiles",{"projection":"SUMMARY","pageSize":1000,"pageNumber":0})
    muts=[p for p in profs if str(p.get("molecularAlterationType","")).upper()=="MUTATION_EXTENDED"]
    if not muts: return study+"_mutations"
    muts.sort(key=lambda p:(0 if str(p.get("molecularProfileId","")).endswith("_mutations") else 1,str(p.get("molecularProfileId",""))))
    return muts[0].get("molecularProfileId")

def sample_list(study):
    d=get(f"/sample-lists/{study}_sequenced",{"projection":"DETAILED"},allow404=True)
    if d and d.get("sampleIds"): return study+"_sequenced",d["sampleIds"],"mutation-sequenced"
    lists=get(f"/studies/{study}/sample-lists",{"projection":"DETAILED","pageSize":1000,"pageNumber":0})
    scored=[]
    for x in lists:
        lid=x.get("sampleListId",""); name=(x.get("name") or "").lower(); cat=(x.get("category") or "").lower()
        sc=0
        if "sequenced" in lid.lower() or "sequenced" in name: sc+=10
        if "mutation" in name or "mutation" in cat: sc+=7
        if lid.endswith("_all"): sc+=1
        scored.append((sc,lid,x.get("sampleIds") or []))
    scored.sort(reverse=True)
    if scored:
        sc,lid,ids=scored[0]
        if not ids:
            d=get(f"/sample-lists/{lid}",{"projection":"DETAILED"},allow404=True) or {}
            ids=d.get("sampleIds") or []
        return lid,ids,"best-available"
    return study+"_all",[],"catalog-fallback"

def mutations(profile,list_id):
    # Follow cBioPortal's documented GET example exactly: molecularProfileId
    # is in the path; sampleListId + projection are the only query arguments.
    rows=get(f"/molecular-profiles/{profile}/mutations",{
        "sampleListId":list_id,
        "projection":"DETAILED"
    })
    yield from rows

def symbol(m):
    g=m.get("gene") or {}
    return (g.get("hugoGeneSymbol") or m.get("hugoGeneSymbol") or "").upper()

def main():
    cat=json.loads(CATALOG.read_text(encoding="utf-8"))
    selected=cat["defaultStudyIds"][:10]
    byid={s["studyId"]:s for s in cat["studies"]}

    matrix={g:{} for g in GENES}
    event_matrix={g:{} for g in GENES}
    module_matrix={m:{} for m in MODULES}
    studies=[]; errors=[]; mutation_type_counts={}

    for sid in selected:
        meta=byid[sid]
        prof=mutation_profile(sid)
        lid,sample_ids,denom_source=sample_list(sid)
        denom_set=set(map(str,sample_ids))
        denom=len(denom_set) if denom_set else int(meta.get("sampleCount") or 0)
        retrieval_list=sid+"_all"

        mutated=defaultdict(set); events=defaultdict(int); vartypes=defaultdict(int); total_events=0
        fetch_ok=True
        try:
            for m in mutations(prof,retrieval_list):
                samp=str(m.get("sampleId") or "")
                if denom_set and samp not in denom_set:
                    continue
                total_events+=1
                sym=symbol(m)
                vt=str(m.get("mutationType") or m.get("variantClassification") or "Other")
                vartypes[vt]+=1
                if sym in GENES:
                    if samp: mutated[sym].add(samp)
                    events[sym]+=1
        except Exception as e:
            fetch_ok=False
            errors.append({"studyId":sid,"error":repr(e),"profile":prof,"retrievalSampleListId":retrieval_list,"denominatorSampleListId":lid})

        for g in GENES:
            if fetch_ok:
                n=len(mutated[g]); pct=(100*n/denom) if denom else None
                matrix[g][sid]=pct; event_matrix[g][sid]=events[g]
            else:
                matrix[g][sid]=None; event_matrix[g][sid]=None

        for mod,genes in MODULES.items():
            if fetch_ok:
                union=set()
                for g in genes: union |= mutated[g]
                module_matrix[mod][sid]=(100*len(union)/denom) if denom else None
            else:
                module_matrix[mod][sid]=None

        mutation_type_counts[sid]=dict(sorted(vartypes.items(),key=lambda kv:kv[1],reverse=True)[:12])
        studies.append({
            "studyId":sid,"name":meta.get("name",sid),"cancerTypeName":meta.get("cancerTypeName",""),
            "catalogSampleCount":int(meta.get("sampleCount") or 0),
            "mutationProfileId":prof,"sampleListId":lid,"retrievalSampleListId":retrieval_list,"denominatorSource":denom_source,
            "mutationSequencedDenominator":denom,"mutationEventsFetched":total_events,
            "mutationFetchOk":fetch_ok
        })
        time.sleep(.15)

    gene_summary=[]
    for g in GENES:
        vals=[v for v in matrix[g].values() if v is not None]
        module=next(m for m,gs in MODULES.items() if g in gs)
        gene_summary.append({
            "gene":g,"module":module,
            "meanPercent":sum(vals)/len(vals) if vals else None,
            "medianPercent":float(pd.Series(vals).median()) if vals else None,
            "maxPercent":max(vals) if vals else None,
            "studiesWithMutation":sum(1 for v in vals if v and v>0)
        })
    gene_summary.sort(key=lambda x:(x["meanPercent"] is not None,x["meanPercent"] or -1),reverse=True)

    # Long-format downloadable matrix
    long=[]
    for g in GENES:
        mod=next(m for m,gs in MODULES.items() if g in gs)
        for s in studies:
            sid=s["studyId"]
            long.append({
                "studyId":sid,"studyName":s["name"],"cancerType":s["cancerTypeName"],
                "gene":g,"module":mod,
                "mutationPercent":matrix[g][sid],
                "mutationEvents":event_matrix[g][sid],
                "denominator":s["mutationSequencedDenominator"],
                "denominatorSource":s["denominatorSource"]
            })
    pd.DataFrame(long).to_csv(DATA/"disease_bioelectric_gene_study_matrix.csv",index=False)

    module_rows=[]
    for mod in MODULES:
        for s in studies:
            sid=s["studyId"]
            module_rows.append({
                "studyId":sid,"studyName":s["name"],"cancerType":s["cancerTypeName"],
                "module":mod,"percentSamplesWithAnyPanelGeneMutation":module_matrix[mod][sid],
                "denominator":s["mutationSequencedDenominator"]
            })
    pd.DataFrame(module_rows).to_csv(DATA/"disease_bioelectric_module_matrix.csv",index=False)

    payload={
        "source":"cBioPortal public REST API",
        "apiBase":BASE,
        "analysisType":"advanced exploratory cross-study mutation bridge",
        "signatureStatus":"candidate mechanistic panel; NOT frozen Bioelectric Gene Signature",
        "generatedStudyIds":selected,
        "modules":MODULES,
        "studies":studies,
        "geneByStudyPercent":matrix,
        "geneByStudyEventCount":event_matrix,
        "moduleByStudyPercent":module_matrix,
        "mutationTypeCounts":mutation_type_counts,
        "geneSummary":gene_summary,
        "errors":errors,
        "downloads":{
            "geneStudyMatrix":"data/disease_bioelectric_gene_study_matrix.csv",
            "moduleMatrix":"data/disease_bioelectric_module_matrix.csv"
        },
        "interpretation":"Cancer somatic-mutation frequencies provide disease-genomic context only. Failed API retrievals are encoded as null/NA, never as zero. Values do not establish causation of neuronal electrical phenotypes and should not be extrapolated to non-cancer neurological disease."
    }
    (DATA/"disease_bioelectric_bridge.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    print(json.dumps({"studies":len(studies),"genes":len(GENES),"errors":len(errors),"top":gene_summary[:8]},indent=2))

if __name__=="__main__": main()
