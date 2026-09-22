"""Assemble NEURO-BEAM end-to-end workflow and prediction release manifest."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"data"

def loadj(name):
    return json.loads((D/name).read_text(encoding="utf-8"))

def main():
    discovery=loadj("visual_cortex_discovery.json")
    stability=loadj("visual_cortex_stability_validation.json")
    grouped=loadj("ml_grouped_cv_summary.json")
    external=loadj("m1_external_validation_summary.json")
    calibration=loadj("ml_calibration_uncertainty.json")
    controls=loadj("ml_negative_controls.json")
    release=loadj("release_status.json")
    pareto=loadj("neurobeam_pareto_evidence.json")
    neuro=loadj("neurological_disease_evidence.json")

    cal_rows=calibration.get("metrics", calibration.get("summary", calibration.get("calibrationSummary", [])))
    cov_rows=calibration.get("coverageSummary", [])
    cal={(x.get("model"),x.get("target")):x for x in cal_rows}
    cov={(x.get("model"),x.get("target")):x for x in cov_rows}
    neg={x["target"]:x for x in controls.get("comparisons",[])}
    ext={x["target_vis"]:x for x in external.get("metrics",[])}

    # Validated production model = ExtraTrees under grouped subject CV.
    pred=[]
    for x in grouped.get("summary",[]):
        if x.get("model")!="ExtraTrees":
            continue
        t=x["target"]
        c=cal.get(("ExtraTrees",t),{})
        cv=cov.get(("ExtraTrees",t),{})
        e=ext.get(t,{})
        n=neg.get(t,{})
        pred.append({
            "target":t,
            "internal_r2_mean":x.get("r2_mean"),
            "internal_r2_sd":x.get("r2_sd"),
            "internal_spearman_mean":x.get("spearman_mean"),
            "internal_spearman_sd":x.get("spearman_sd"),
            "internal_mae_mean":x.get("mae_mean"),
            "calibration_intercept":c.get("calibration_intercept"),
            "calibration_slope":c.get("calibration_slope"),
            "coverage90":cv.get("coverage90"),
            "coverage95":cv.get("coverage95"),
            "external_m1_spearman":e.get("spearman"),
            "external_m1_r2":e.get("r2"),
            "external_m1_mae":e.get("mae"),
            "signal_over_permutation_delta":n.get("signal_over_null_delta"),
            "leakage_inflation_delta":n.get("leakage_inflation_delta"),
            "external_status":"compatible M1 trait" if e else "not harmonized to M1"
        })
    pd.DataFrame(pred).to_csv(D/"prediction_console.csv",index=False)

    # Pull counts robustly from current evidence outputs.
    tier_counts={}
    if isinstance(pareto,dict):
        for key in ("tierCounts","tier_counts","tiers"):
            if isinstance(pareto.get(key),dict):
                tier_counts=pareto[key];break
    if not tier_counts:
        try:
            pc=pd.read_csv(D/"top500_evidence_tiers.csv")
            col=next(c for c in pc.columns if "tier" in c.lower())
            raw={str(k):int(v) for k,v in pc[col].value_counts().to_dict().items()}
            tier_counts=raw.copy()
            tier_counts["A"]=sum(v for k,v in raw.items() if str(k).strip().upper().startswith("A"))
            tier_counts["B"]=sum(v for k,v in raw.items() if str(k).strip().upper().startswith("B"))
            tier_counts["C"]=sum(v for k,v in raw.items() if str(k).strip().upper().startswith("C"))
        except Exception:
            tier_counts={}

    neuro_overlap=None
    for key in ("genesWithEvidence","genes_with_evidence","nGenesWithEvidence","n_genes_with_evidence"):
        if key in neuro:
            neuro_overlap=neuro[key];break
    if neuro_overlap is None:
        try:
            ng=pd.read_csv(D/"neurological_disease_gene_summary.csv")
            neuro_overlap=int(len(ng))
        except Exception:
            neuro_overlap=None

    stages=[
      {
        "stage":1,"id":"brain-region","title":"Brain region","status":"integrated reference + external validation",
        "evidence":"VIS discovery; M1 external validation; ABC Atlas/MERFISH reserved for spatial projection",
        "primary_n":int(grouped.get("nCells",0)),"secondary_n":int(external.get("nExternalM1",0)),
        "key_result":"Visual cortex is the discovery region; primary motor cortex is held out for external generalization.",
        "guardrail":"ABC Atlas/MERFISH is a spatial reference layer, not same-cell Patch-seq evidence in the current release."
      },
      {
        "stage":2,"id":"neuron-identity","title":"Neuron identity","status":"same-cell measured",
        "evidence":"Patch-seq transcriptomics + electrophysiology; broad neuronal class metadata",
        "primary_n":int(grouped.get("nCells",0)),"secondary_n":int(grouped.get("nSubjects",0)),
        "key_result":f'{grouped.get("nCells",0)} matched neurons from {grouped.get("nSubjects",0)} subjects support subject-grouped inference.',
        "guardrail":"Identity labels are used for stratification/robustness checks, not to define molecular-electrical causality."
      },
      {
        "stage":3,"id":"bioelectric-state","title":"Bioelectric state","status":"measured + unsupervised",
        "evidence":"Electrophysiology; PCA; K-means/GMM/HDBSCAN; bootstrap stability",
        "primary_n":int(discovery.get("qc_neurons",grouped.get("nCells",0))),
        "secondary_n":int(discovery.get("numeric_features_after_qc",0)),
        "key_result":f'Physiology-only discovery retained {discovery.get("numeric_features_after_qc",0)} features; bootstrap ARI={stability.get("bootstrap_ari_mean",float("nan")):.3f}.',
        "guardrail":"Candidate electrical states remain descriptive; unstable/rare states are not assigned biological names."
      },
      {
        "stage":4,"id":"gene-regulation","title":"Gene regulation","status":"same-cell association + evidence tiers",
        "evidence":"1,302-gene Patch-seq matrix; BH-FDR gene–ephys coupling; Top-500/Pareto evidence",
        "primary_n":int(grouped.get("nGenes",0)),"secondary_n":500,
        "key_result":f'{grouped.get("nGenes",0)} genes were tested against measured electrical traits; Top-500 evidence catalog and tiering are available.',
        "guardrail":"Associations are transcriptomic correlates of electrical phenotypes; TF/pathway interpretation is secondary unless directly tested."
      },
      {
        "stage":5,"id":"regulatory-context","title":"Regulatory context","status":"proxy + external context",
        "evidence":"DNA-repair/chromatin gene modules; neurological-disease evidence; 4DN/SMaHT contextual resources",
        "primary_n":int(neuro_overlap or 0),"secondary_n":int(tier_counts.get("A",tier_counts.get("Tier A",0)) or 0),
        "key_result":f'{neuro_overlap or 0} Top-500 genes have neurological-disease evidence; regulatory/chromatin interpretation is carried as contextual evidence.',
        "guardrail":"No same-cell chromatin assay is present in the core Patch-seq cohort; chromatin/DNA-repair claims are proxy/contextual, not directly measured."
      },
      {
        "stage":6,"id":"prediction","title":"Prediction","status":"validated baseline",
        "evidence":"5-fold GroupKFold by subject; ExtraTrees/Ridge; permutation controls; conformal coverage; untouched M1 evaluation",
        "primary_n":len(pred),"secondary_n":int(external.get("nExternalM1",0)),
        "key_result":"ExtraTrees is the current validated production baseline; NeuroBEAM-Net denotes the framework, not an unvalidated deep model.",
        "guardrail":"External M1 rank generalization is trait-dependent and calibration/domain shift can be substantial; do not convert predictions into clinical or causal claims."
      }
    ]
    pd.DataFrame(stages).to_csv(D/"end_to_end_stage_summary.csv",index=False)

    # Overall prediction snapshot.
    strong=sorted(pred,key=lambda x:(x["internal_spearman_mean"] or -1),reverse=True)
    ext_valid=[x for x in pred if x.get("external_m1_spearman") is not None]
    payload={
      "project":"NEURO-BEAM",
      "workflowVersion":"End-to-end release 1.0",
      "stages":stages,
      "prediction":{
        "frameworkName":"NeuroBEAM-Net",
        "validatedModel":"ExtraTrees regression with fold-local top-300 variance genes",
        "split":grouped.get("split"),
        "normalization":grouped.get("normalization"),
        "nCells":grouped.get("nCells"),
        "nSubjects":grouped.get("nSubjects"),
        "nGenes":grouped.get("nGenes"),
        "targets":pred,
        "topInternalTraits":strong[:5],
        "externalM1MeanSpearman":float(np.mean([x["external_m1_spearman"] for x in ext_valid])) if ext_valid else None,
        "externalM1Traits":len(ext_valid),
        "uncertainty":"cross-conformal 90/95% empirical coverage",
        "negativeControls":"subject-grouped evaluation plus response permutation controls"
      },
      "releaseIntegrity":{
        "passed":release.get("passed"),"total":release.get("total"),
        "publicationReadyEngineeringGate":release.get("publicationReady"),
        "interpretation":release.get("interpretation")
      },
      "evidenceLanguage":{
        "measured":"directly present in same-cell/core dataset",
        "external":"tested in a held-out external cohort",
        "proxy":"biological context inferred from gene/pathway evidence, not directly measured",
        "predicted":"model output with empirical validation and uncertainty"
      },
      "guardrail":"This end-to-end release integrates measured, external, proxy and predicted evidence. These evidence classes must not be collapsed into a single causal chain."
    }
    (D/"end_to_end_workflow.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")

    report=["# NEURO-BEAM End-to-End Release Report","",
      "## Workflow","",
      "Brain region → Neuron identity → Bioelectric state → Gene regulation → Regulatory context → Prediction",""]
    for s in stages:
        report += [f'### {s["stage"]}. {s["title"]}',f'- Status: **{s["status"]}**',f'- Evidence: {s["evidence"]}',f'- Key result: {s["key_result"]}',f'- Guardrail: {s["guardrail"]}',""]
    report += ["## Prediction release","",
      f'- Validated production baseline: {payload["prediction"]["validatedModel"]}',
      f'- Validation: {payload["prediction"]["split"]}',
      f'- Cells / subjects / genes: {grouped.get("nCells")} / {grouped.get("nSubjects")} / {grouped.get("nGenes")}',
      f'- Compatible external M1 traits: {len(ext_valid)}',
      f'- Mean external M1 Spearman across compatible traits: {payload["prediction"]["externalM1MeanSpearman"]:.3f}' if ext_valid else '- External M1: not available',
      "",
      "## Interpretation boundary","",
      payload["guardrail"]]
    (ROOT/"docs"/"end_to_end_release_report.md").write_text("\n".join(report),encoding="utf-8")
    print(json.dumps({"stages":len(stages),"predictionTargets":len(pred),"releaseChecks":f'{release.get("passed")}/{release.get("total")}',"externalM1Traits":len(ext_valid)},indent=2))

if __name__=="__main__":
    main()
