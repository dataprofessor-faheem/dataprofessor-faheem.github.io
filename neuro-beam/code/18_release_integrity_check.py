"""NEURO-BEAM CBEF release-integrity gate."""
from pathlib import Path
import json
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"data"

def require(cond,msg):
    if not cond:
        raise RuntimeError("RELEASE INTEGRITY FAILURE: "+msg)

def main():
    top=pd.read_csv(D/"top500_gene_catalog.csv")
    cancer=pd.read_csv(D/"top500_cancer_matrix.csv")
    full=pd.read_csv(D/"cbef_full_gene_catalog.csv")
    full_cancer=pd.read_csv(D/"cbef_full_cancer_matrix.csv")
    bio=pd.read_csv(D/"top500_bioelectric_matrix.csv")
    cat=json.loads((D/"top500_discovery_catalog.json").read_text())
    models=json.loads((D/"top500_dynamic_models.json").read_text()).get("models",[])

    require(len(top)==500,f"expected 500 ranked genes, found {len(top)}")
    require(top["gene"].nunique()==500,"Top-500 genes are not unique")
    require(top["rank"].tolist()==list(range(1,501)),"ranks must be exactly 1..500")
    require(len(cat.get("studies",[]))==10,f"expected 10 cohorts, found {len(cat.get('studies',[]))}")
    require(cat.get("cohortCoverage") in (None,"10/10"),f"incomplete cohort coverage: {cat.get('cohortCoverage')}")
    require(not cat.get("failedCohorts",[]),f"failed cohorts recorded: {cat.get('failedCohorts')}")
    require(len(cancer)==5000,f"expected 5,000 Top500 gene×cohort rows, found {len(cancer)}")
    require(cancer["study_id"].nunique()==10,"Top500 cancer matrix does not contain 10 unique cohorts")
    require(cancer["gene"].nunique()==500,"Top500 cancer matrix does not contain 500 unique genes")
    require(cancer["mutation_percent"].notna().all(),"Top500 cancer matrix contains missing mutation prevalence")
    require(cancer["mutation_sequenced_n"].gt(0).all(),"invalid cancer denominators")
    require(len(full)>=500,"full CBEF gene universe smaller than Top500")
    require(full_cancer["study_id"].nunique()==10,"full cancer matrix missing cohorts")
    require(full_cancer["mutation_percent"].notna().all(),"full cancer matrix contains missing mutation prevalence")
    require(len(models)==500,f"expected 500 dynamic models, found {len(models)}")
    require(len(bio)>500,"bioelectric matrix unexpectedly small")
    required={"cbef_discovery_score","bioelectric_evidence_score","cancer_evidence_score","cross_domain_synergy","best_electrical_feature","best_rho","best_feature_q"}
    require(required.issubset(top.columns),f"missing Top500 columns: {sorted(required-set(top.columns))}")

    summary={
      "status":"PASS","top500Genes":500,"cohorts":10,
      "top500CancerRows":len(cancer),"fullMappedGenes":len(full),
      "fullCancerRows":len(full_cancer),"dynamicModels":len(models),
      "bioelectricRows":len(bio)
    }
    (D/"cbef_release_integrity.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))

if __name__=="__main__": main()
