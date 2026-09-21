"""Build full Cancer × Gene × Bioelectric Signal signature cube for NEURO-BEAM."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
BIO=DATA/"bioelectric_disease_bridge.json"
DIS=DATA/"disease_bioelectric_bridge.json"
ASSOC=DATA/"bioelectric_gene_associations.csv"

def main():
    bio=json.loads(BIO.read_text(encoding="utf-8"))
    dis=json.loads(DIS.read_text(encoding="utf-8"))
    assoc=pd.read_csv(ASSOC)

    studies={s["studyId"]:s for s in dis["studies"]}
    gene_scores={x["gene"]:x for x in bio.get("geneBioelectricScores",[])}
    shared=bio.get("candidatePanelSharedGenes",[])

    rows=[]
    for gene in shared:
        mouse_gene=gene_scores.get(gene,{}).get("mouseGene",gene.title())
        a=assoc[assoc["gene"].astype(str).str.upper()==mouse_gene.upper()].copy()
        if a.empty:
            continue
        for _,ar in a.iterrows():
            for sid,s in studies.items():
                mut=dis.get("geneByStudyPercent",{}).get(gene,{}).get(sid)
                gs=gene_scores.get(gene,{})
                rho=float(ar["rho"]) if pd.notna(ar["rho"]) else np.nan
                mutfrac=(float(mut)/100.0) if mut is not None else np.nan
                rows.append({
                    "study_id":sid,
                    "study_name":s.get("name",sid),
                    "cancer_type":s.get("cancerTypeName",""),
                    "mutation_sequenced_n":s.get("mutationSequencedDenominator"),
                    "denominator_source":s.get("denominatorSource",""),
                    "mutation_profile_id":s.get("mutationProfileId",""),
                    "gene":gene,
                    "mouse_gene":mouse_gene,
                    "electrical_feature":ar["feature"],
                    "spearman_rho":rho,
                    "p_value":ar["p"],
                    "bh_fdr_q":ar["q"],
                    "matched_neuron_n":ar["n"],
                    "mutation_percent":mut,
                    "signed_mutation_bioelectric_score":(mutfrac*rho) if np.isfinite(mutfrac) and np.isfinite(rho) else np.nan,
                    "absolute_mutation_bioelectric_score":(mutfrac*abs(rho)) if np.isfinite(mutfrac) and np.isfinite(rho) else np.nan,
                    "bioelectric_coupling_score":gs.get("bioelectricCouplingScore"),
                    "best_electrical_feature":gs.get("bestFeature"),
                    "same_direction_fraction_across_classes":gs.get("sameDirectionFraction"),
                    "classes_tested":gs.get("classesTested"),
                    "source_patchseq":"Allen visual cortex Patch-seq processed via scMNC companion data",
                    "source_cancer":"cBioPortal public REST API",
                    "integration_status":"exploratory independent-source integration"
                })

    df=pd.DataFrame(rows)
    df.to_csv(DATA/"cancer_gene_bioelectric_signature_cube.csv",index=False)

    # compact JSON for browser
    payload={
      "nRows":len(df),
      "studies":[{
          "studyId":sid,
          "name":s.get("name",sid),
          "cancerTypeName":s.get("cancerTypeName",""),
          "mutationSequencedDenominator":s.get("mutationSequencedDenominator")
      } for sid,s in studies.items()],
      "genes":sorted(df["gene"].unique().tolist()),
      "electricalFeatures":sorted(df["electrical_feature"].unique().tolist()),
      "rows":df.replace({np.nan:None}).to_dict(orient="records"),
      "downloads":{
        "fullCube":"data/cancer_gene_bioelectric_signature_cube.csv",
        "geneAssociations":"data/bioelectric_gene_associations.csv",
        "geneScores":"data/bioelectric_gene_scores.csv",
        "diseaseScores":"data/disease_bioelectric_scores.csv"
      },
      "interpretation":"All cross-domain scores are exploratory and association-based. Cancer mutation prevalence does not establish a causal effect on neuronal electrophysiology."
    }
    (DATA/"cancer_gene_bioelectric_signature_cube.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    print(json.dumps({"rows":len(df),"genes":payload["genes"],"features":len(payload["electricalFeatures"]),"studies":len(payload["studies"])},indent=2))

if __name__=="__main__": main()
