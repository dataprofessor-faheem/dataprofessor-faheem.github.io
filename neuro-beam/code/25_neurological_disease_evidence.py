"""Neurological-disease evidence projection from Open Targets Platform GraphQL.

Evidence type: integrated target-disease association score.
This is kept separate from cancer mutation prevalence.
"""
from __future__ import annotations
import json,time
from pathlib import Path
import requests,pandas as pd

ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/"data"
API="https://api.platform.opentargets.org/api/v4/graphql"
DISEASES={
  "Alzheimer disease":"Alzheimer disease",
  "Parkinson disease":"Parkinson disease",
  "epilepsy":"epilepsy",
  "amyotrophic lateral sclerosis":"amyotrophic lateral sclerosis",
  "stroke":"stroke"
}
S=requests.Session();S.headers.update({"content-type":"application/json","User-Agent":"NEURO-BEAM/3.0"})

SEARCH_Q="""query Search($q:String!){ search(queryString:$q, entityNames:[\"disease\"], page:{index:0,size:10}){ hits{ id name entity } } }"""
ASSOC_Q="""query Assoc($id:String!){ disease(efoId:$id){ id name associatedTargets(page:{index:0,size:1000}){ count rows{ score target{ id approvedSymbol approvedName } } } } }"""

def gql(query,variables):
    r=S.post(API,json={"query":query,"variables":variables},timeout=120)
    r.raise_for_status();j=r.json()
    if j.get("errors"):raise RuntimeError(j["errors"])
    return j["data"]

def main():
    top=pd.read_csv(DATA/"top500_gene_catalog.csv")
    topgenes=set(top.gene.astype(str))
    rows=[];meta=[];errors=[]
    for label,q in DISEASES.items():
        try:
            s=gql(SEARCH_Q,{"q":q})
            hits=s.get("search",{}).get("hits",[])
            if not hits:raise RuntimeError("No disease search hit")
            # Prefer exact/near-exact disease name.
            hits=sorted(hits,key=lambda h:(0 if str(h.get("name","")).lower()==q.lower() else 1,len(str(h.get("name","")))))
            hit=hits[0];did=hit["id"]
            a=gql(ASSOC_Q,{"id":did})
            dis=a.get("disease") or {}
            assoc=(dis.get("associatedTargets") or {}).get("rows") or []
            meta.append({"requested":label,"query":q,"diseaseId":did,"resolvedName":dis.get("name"),"targetCount":(dis.get("associatedTargets") or {}).get("count")})
            for x in assoc:
                t=x.get("target") or {};gene=t.get("approvedSymbol")
                if gene in topgenes:
                    rows.append({
                      "disease":label,"disease_id":did,"resolved_disease_name":dis.get("name"),
                      "gene":gene,"target_id":t.get("id"),"target_name":t.get("approvedName"),
                      "open_targets_association_score":x.get("score"),
                      "evidence_type":"Open Targets integrated target-disease association"
                    })
        except Exception as e:
            errors.append({"disease":label,"error":repr(e)})
        time.sleep(.15)
    df=pd.DataFrame(rows)
    if len(df):df.to_csv(DATA/"neurological_disease_target_evidence.csv",index=False)
    else:pd.DataFrame(columns=["disease","gene","open_targets_association_score"]).to_csv(DATA/"neurological_disease_target_evidence.csv",index=False)

    # wide matrix and per-gene summary
    if len(df):
        mat=df.pivot_table(index="gene",columns="disease",values="open_targets_association_score",aggfunc="max").reindex(sorted(topgenes))
        mat.to_csv(DATA/"neurological_disease_gene_matrix.csv")
        sm=df.groupby("gene").agg(
            neuro_disease_max_score=("open_targets_association_score","max"),
            neuro_disease_mean_score=("open_targets_association_score","mean"),
            neuro_disease_count=("disease","nunique")
        ).reset_index()
        sm.to_csv(DATA/"neurological_disease_gene_summary.csv",index=False)
    else:
        pd.DataFrame(index=sorted(topgenes)).to_csv(DATA/"neurological_disease_gene_matrix.csv")
        sm=pd.DataFrame(columns=["gene","neuro_disease_max_score","neuro_disease_mean_score","neuro_disease_count"])
        sm.to_csv(DATA/"neurological_disease_gene_summary.csv",index=False)

    payload={
      "source":"Open Targets Platform GraphQL API",
      "evidenceType":"integrated target-disease association score",
      "diseases":meta,"errors":errors,
      "top500GenesWithAnyNeurologicalEvidence":int(df.gene.nunique()) if len(df) else 0,
      "rows":df.to_dict(orient="records") if len(df) else [],
      "guardrail":"Open Targets association scores integrate heterogeneous genetic/functional evidence and are not mutation prevalence, effect size, or neuronal physiology."
    }
    (DATA/"neurological_disease_evidence.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    print(json.dumps({"diseases":meta,"errors":errors,"genes":payload["top500GenesWithAnyNeurologicalEvidence"],"rows":len(df)},indent=2))

if __name__=="__main__":main()
