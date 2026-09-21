"""NEURO-BEAM publication release audit."""
from pathlib import Path
import json
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];D=ROOT/"data"
checks=[]
def add(name,ok,detail):checks.append({"check":name,"pass":bool(ok),"detail":detail})
def exists(name):return (D/name).exists()

# Top500
try:
    top=json.loads((D/"top500_cancer_bioelectric_genes.json").read_text())
    add("top500_catalog_500",len(top.get("top500",[]))==500,f"n={len(top.get('top500',[]))}")
    ranks=[x["rank"] for x in top["top500"]];genes=[x["gene"] for x in top["top500"]]
    add("top500_unique_ranks",len(set(ranks))==500,"unique rank count="+str(len(set(ranks))))
    add("top500_unique_genes",len(set(genes))==500,"unique gene count="+str(len(set(genes))))
except Exception as e:add("top500_catalog_500",False,repr(e))

for fn,expected in [
  ("top500_cancer_matrix.csv",5000),
  ("top500_bioelectric_matrix.csv",9000)
]:
    try:
        x=pd.read_csv(D/fn);add(fn+"_rows",len(x)==expected,f"rows={len(x)} expected={expected}")
    except Exception as e:add(fn+"_rows",False,repr(e))

try:
    mod=json.loads((D/"top500_dynamic_model_library.json").read_text())
    add("dynamic_model_library_500",len(mod.get("genes",[]))==500,f"n={len(mod.get('genes',[]))}")
except Exception as e:add("dynamic_model_library_500",False,repr(e))

try:
    ml=json.loads((D/"ml_grouped_cv_summary.json").read_text())
    add("grouped_cv_subjects",ml.get("nSubjects",0)>100,f"subjects={ml.get('nSubjects')}")
    add("grouped_cv_cells",ml.get("nCells",0)>1000,f"cells={ml.get('nCells')}")
except Exception as e:add("grouped_cv",False,repr(e))

try:
    ext=json.loads((D/"m1_external_validation_summary.json").read_text())
    add("external_m1_cells",ext.get("nExternalM1",0)>500,f"n={ext.get('nExternalM1')}")
    add("external_m1_metrics",len(ext.get("metrics",[]))>=5,f"metrics={len(ext.get('metrics',[]))}")
except Exception as e:
    add("external_m1_cells",False,"external validation not yet available: "+repr(e))
    add("external_m1_metrics",False,"external validation not yet available")

required=[
 "bioelectric_gene_associations.csv","cancer_gene_bioelectric_signature_cube.csv",
 "top500_cancer_bioelectric_genes.csv","top500_dynamic_model_parameters.csv",
 "ml_grouped_cv_summary.csv","scientific_release_placeholder"
]
for fn in required[:-1]:
    add("file_"+fn,exists(fn),"present" if exists(fn) else "missing")

status={
 "checks":checks,
 "passed":sum(x["pass"] for x in checks),
 "total":len(checks),
 "publicationReady":all(x["pass"] for x in checks),
 "interpretation":"PublicationReady is an engineering/integrity gate, not a prediction of journal acceptance."
}
(D/"release_status.json").write_text(json.dumps(status,indent=2))
print(json.dumps(status,indent=2))
