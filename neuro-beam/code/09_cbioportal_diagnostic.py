import json,requests
from pathlib import Path
BASE="https://www.cbioportal.org/api"
study="gbm_tcga_pan_can_atlas_2018"
S=requests.Session();S.headers.update({"accept":"application/json","User-Agent":"NEURO-BEAM-diagnostic/1.0"})
def g(path,params=None):
    r=S.get(BASE+path,params=params,timeout=90)
    out={"url":r.url,"status":r.status_code,"text":r.text[:1500]}
    if r.ok:
        try: out["json"]=r.json()
        except: pass
    return out
res={}
res["profiles"]=g(f"/studies/{study}/molecular-profiles",{"projection":"DETAILED"})
res["sample_lists"]=g(f"/studies/{study}/sample-lists",{"projection":"DETAILED"})
profiles=[]
if "json" in res["profiles"]:
    for p in res["profiles"]["json"]:
        if "MUTATION" in str(p.get("molecularAlterationType","")).upper():
            profiles.append(p.get("molecularProfileId"))
lists=[]
if "json" in res["sample_lists"]:
    for x in res["sample_lists"]["json"]:
        lid=x.get("sampleListId")
        if lid and (lid.endswith("_all") or "sequenced" in lid.lower()):
            lists.append(lid)
res["tests"]=[]
for p in profiles[:5]:
    for lid in lists[:5]:
        res["tests"].append({"profile":p,"list":lid,"result":g(f"/molecular-profiles/{p}/mutations",{"sampleListId":lid,"projection":"DETAILED"})})
Path("neuro-beam/data/cbioportal_gbm_diagnostic.json").write_text(json.dumps(res,indent=2))
print(json.dumps({"profiles":profiles,"lists":lists,"tests":[{"profile":x["profile"],"list":x["list"],"status":x["result"]["status"]} for x in res["tests"]]},indent=2))
