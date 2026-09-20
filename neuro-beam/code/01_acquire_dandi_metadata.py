"""Fetch DANDI dandiset metadata and asset inventories without downloading raw NWB files."""
from __future__ import annotations
import json
from pathlib import Path
import requests
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "source"
OUT.mkdir(parents=True, exist_ok=True)
DANDISETS = ["000020", "001455", "000008"]
BASE = "https://api.dandiarchive.org/api"
def get_json(url, params=None):
    r = requests.get(url, params=params, timeout=60); r.raise_for_status(); return r.json()
def latest_version(dandiset_id):
    ds = get_json(f"{BASE}/dandisets/{dandiset_id}/")
    published = ds.get("most_recent_published_version")
    if published: return published["version"] if isinstance(published, dict) else str(published)
    return "draft"
def asset_inventory(dandiset_id, version):
    url=f"{BASE}/dandisets/{dandiset_id}/versions/{version}/assets/"; rows=[]; params={"page_size":1000}
    while url:
        payload=get_json(url,params=params); params=None
        for a in payload.get("results",[]):
            rows.append({"asset_id":a.get("asset_id") or a.get("identifier"),"path":a.get("path"),"size":a.get("size"),"created":a.get("created"),"modified":a.get("modified")})
        url=payload.get("next")
    return pd.DataFrame(rows)
def main():
    summary=[]
    for did in DANDISETS:
        version=latest_version(did); meta=get_json(f"{BASE}/dandisets/{did}/versions/{version}/")
        with open(OUT/f"dandi_{did}_{version}_metadata.json","w",encoding="utf-8") as f: json.dump(meta,f,indent=2)
        inv=asset_inventory(did,version); inv.to_csv(OUT/f"dandi_{did}_{version}_assets.csv",index=False)
        summary.append({"dandiset":did,"version":version,"n_assets":len(inv),"bytes":int(inv["size"].fillna(0).sum()) if not inv.empty else 0})
    pd.DataFrame(summary).to_csv(OUT/"dandi_inventory_summary.csv",index=False)
    print(pd.DataFrame(summary).to_string(index=False))
if __name__=="__main__": main()