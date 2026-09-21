"""Build a public cBioPortal study catalog for the NEURO-BEAM disease explorer.

The catalog is metadata only. It enables client-side selection of up to 10
cancer disease/study cohorts. Full genomic exploration remains linked to the
authoritative cBioPortal site/API.
"""
from __future__ import annotations
import json
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data"
OUT.mkdir(parents=True,exist_ok=True)
BASE="https://www.cbioportal.org/api"

def get_json(path, params=None):
    r=requests.get(BASE+path,params=params,timeout=90,headers={"accept":"application/json"})
    r.raise_for_status()
    return r.json()

def main():
    studies=get_json("/studies",{"projection":"SUMMARY","pageSize":10000,"pageNumber":0})
    try:
        cancer_types=get_json("/cancer-types",{"projection":"SUMMARY","pageSize":1000,"pageNumber":0})
    except Exception:
        cancer_types=[]
    ct={x.get("cancerTypeId"):x for x in cancer_types if isinstance(x,dict)}

    rows=[]
    for s in studies:
        sid=s.get("studyId") or s.get("id")
        if not sid: continue
        ctid=s.get("cancerTypeId") or ""
        cmeta=ct.get(ctid,{})
        rows.append({
            "studyId":sid,
            "name":s.get("name") or sid,
            "description":s.get("description") or "",
            "cancerTypeId":ctid,
            "cancerTypeName":cmeta.get("name") or ctid,
            "sampleCount":s.get("allSampleCount") or s.get("sampleCount") or 0,
            "referenceGenome":s.get("referenceGenome") or "",
            "public":bool(s.get("publicStudy",True)),
            "cbioSummaryUrl":f"https://www.cbioportal.org/study/summary?id={sid}"
        })
    rows.sort(key=lambda x:(str(x["cancerTypeName"]).lower(),str(x["name"]).lower()))

    preferred=[
        "gbm_tcga_pan_can_atlas_2018",
        "lgg_tcga_pan_can_atlas_2018",
        "brca_tcga_pan_can_atlas_2018",
        "luad_tcga_pan_can_atlas_2018",
        "coadread_tcga_pan_can_atlas_2018",
        "paad_tcga_pan_can_atlas_2018",
        "skcm_tcga_pan_can_atlas_2018",
        "prad_tcga_pan_can_atlas_2018",
        "ucec_tcga_pan_can_atlas_2018",
        "ov_tcga_pan_can_atlas_2018"
    ]
    byid={r["studyId"]:r for r in rows}
    defaults=[x for x in preferred if x in byid]
    if len(defaults)<10:
        used_ct={byid[x]["cancerTypeId"] for x in defaults}
        candidates=sorted(rows,key=lambda x:int(x.get("sampleCount") or 0),reverse=True)
        for x in candidates:
            if len(defaults)>=10: break
            if x["studyId"] in defaults: continue
            if x["cancerTypeId"] in used_ct: continue
            defaults.append(x["studyId"]); used_ct.add(x["cancerTypeId"])

    payload={
        "source":"cBioPortal public REST API",
        "apiBase":BASE,
        "generatedStudyCount":len(rows),
        "maxUserSelection":10,
        "defaultStudyIds":defaults[:10],
        "studies":rows,
        "scopeNote":"cBioPortal is an oncology genomics resource. Non-cancer neurological diseases require separate disease-specific public datasets and are not represented as cBioPortal cohorts."
    }
    (OUT/"cbioportal_study_catalog.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    print(json.dumps({"studies":len(rows),"defaults":defaults[:10]},indent=2))

if __name__=="__main__":
    main()
