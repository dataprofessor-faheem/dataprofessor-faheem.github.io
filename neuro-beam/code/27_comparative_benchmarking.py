"""NEURO-BEAM analytical and comparative benchmarking release."""
from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"data"
DOC=ROOT/"docs"

def J(name): return json.loads((D/name).read_text(encoding="utf-8"))

def safe_mean(xs):
    xs=[float(x) for x in xs if x is not None and np.isfinite(float(x))]
    return float(np.mean(xs)) if xs else None

def main():
    broad=J("predictive_benchmark.json")
    grouped=J("ml_grouped_cv_summary.json")
    ext=J("m1_external_validation_summary.json")
    cal=J("ml_calibration_uncertainty.json")
    neg=J("ml_negative_controls.json")
    cbef=J("cbef_multitask_benchmark.json")
    sens=J("cbef_sensitivity_summary.json")
    beam=J("beam_factor_results.json")
    release=J("release_status.json")
    pareto=J("neurobeam_pareto_evidence.json")

    # 1) Broad 18-trait model benchmark.
    model_rows=[]
    for x in broad.get("models",[]):
        genes=int(x.get("n_genes") or 0)
        rho=float(x.get("mean_trait_spearman"))
        r2=float(x.get("mean_trait_r2"))
        model_rows.append({
            "scope":"18-trait broad",
            "model":x["model"],
            "n_genes":genes,
            "n_traits":int(x.get("traits") or 0),
            "mean_spearman":rho,
            "mean_r2":r2,
            "median_r2":x.get("median_trait_r2"),
            "mean_mae_unscaled":x.get("mean_trait_mae"),
            "spearman_per_100_genes":rho/(genes/100) if genes else None,
            "r2_per_100_genes":r2/(genes/100) if genes else None
        })
    mb=pd.DataFrame(model_rows).sort_values("mean_spearman",ascending=False)
    mb.to_csv(D/"benchmark_model_comparison.csv",index=False)

    # 2) Strict 11-trait grouped benchmark.
    strict=pd.DataFrame(grouped.get("summary",[]))
    strict.to_csv(D/"benchmark_grouped_trait_comparison.csv",index=False)
    strict_model=[]
    for model,g in strict.groupby("model"):
        strict_model.append({
            "model":model,
            "n_traits":len(g),
            "mean_spearman":float(g.spearman_mean.mean()),
            "median_spearman":float(g.spearman_mean.median()),
            "mean_r2":float(g.r2_mean.mean()),
            "median_r2":float(g.r2_mean.median()),
            "traits_r2_positive":int((g.r2_mean>0).sum()),
            "traits_spearman_ge_0_6":int((g.spearman_mean>=0.6).sum())
        })
    strict_model=pd.DataFrame(strict_model).sort_values("mean_spearman",ascending=False)
    strict_model.to_csv(D/"benchmark_grouped_model_summary.csv",index=False)

    # Per-trait winner under grouped CV.
    winners=[]
    for trait,g in strict.groupby("target"):
        g=g.sort_values("spearman_mean",ascending=False)
        top=g.iloc[0]
        second=g.iloc[1] if len(g)>1 else None
        winners.append({
            "trait":trait,
            "best_model":top["model"],
            "best_spearman":float(top["spearman_mean"]),
            "best_r2":float(top["r2_mean"]),
            "runner_up_model":None if second is None else second["model"],
            "spearman_margin":None if second is None else float(top["spearman_mean"]-second["spearman_mean"])
        })
    pd.DataFrame(winners).to_csv(D/"benchmark_trait_winners.csv",index=False)

    # 3) External generalization.
    ext_rows=[]
    for x in ext.get("metrics",[]):
        ext_rows.append({
            "target":x["target_vis"],
            "target_m1":x["target_m1"],
            "n_m1":x["n_m1"],
            "spearman":x["spearman"],
            "r2":x["r2"],
            "mae":x["mae"],
            "rank_transfer_strength":"strong" if abs(x["spearman"])>=0.6 else "moderate" if abs(x["spearman"])>=0.4 else "limited",
            "absolute_scale_status":"positive R2" if x["r2"]>0 else "domain shift / poor absolute calibration"
        })
    ext_df=pd.DataFrame(ext_rows)
    ext_df.to_csv(D/"benchmark_external_m1.csv",index=False)

    # 4) Calibration and uncertainty.
    cal_metrics=pd.DataFrame(cal.get("metrics",[]))
    coverage=pd.DataFrame(cal.get("coverageSummary",[]))
    cal_et=cal_metrics[cal_metrics.model=="ExtraTrees"].copy()
    cov_et=coverage[coverage.model=="ExtraTrees"].copy()
    calib=cal_et.merge(cov_et,on=["model","target"],how="outer")
    calib.to_csv(D/"benchmark_calibration_uncertainty.csv",index=False)

    # 5) Negative controls.
    neg_df=pd.DataFrame(neg.get("comparisons",[]))
    neg_df.to_csv(D/"benchmark_negative_controls.csv",index=False)

    # 6) CBEF latent prior comparison.
    cbef_df=pd.DataFrame(cbef.get("models",[]))
    cbef_df.to_csv(D/"benchmark_cbef_latent_models.csv",index=False)

    # 7) Multi-view / stability metrics.
    ablations=pd.DataFrame(sens.get("ablations",[]))
    ablations.to_csv(D/"benchmark_cbef_ablations.csv",index=False)

    # 8) Aggregate, objective-specific findings (not one opaque composite score).
    best_broad=mb.iloc[0].to_dict()
    best_strict=strict_model.iloc[0].to_dict()
    ext_mean=safe_mean(ext_df.spearman.tolist())
    ext_abs_mean=safe_mean([abs(x) for x in ext_df.spearman.tolist()])
    cov90=safe_mean(cov_et.coverage90.tolist())
    cov95=safe_mean(cov_et.coverage95.tolist())
    null_delta=safe_mean(neg_df.signal_over_null_delta.tolist())
    leak_delta=safe_mean([abs(x) for x in neg_df.leakage_inflation_delta.tolist()])
    tier_counts=pareto.get("counts",{})
    cbe_sens=sens.get("weightSensitivity",{})
    boot=sens.get("cohortBootstrap",{})
    perm=sens.get("permutationNegativeControl",{})

    # Trait strengths.
    et=strict[strict.model=="ExtraTrees"].sort_values("spearman_mean",ascending=False)
    strong_traits=et[et.spearman_mean>=0.8]["target"].tolist()
    weak_traits=et[et.spearman_mean<0.45]["target"].tolist()

    # External strengths / weaknesses.
    ext_sorted=ext_df.reindex(ext_df.spearman.abs().sort_values(ascending=False).index)
    ext_top=ext_sorted.head(4).to_dict(orient="records")
    ext_low=ext_sorted.tail(3).to_dict(orient="records")

    benchmark={
      "project":"NEURO-BEAM",
      "benchmarkVersion":"1.0",
      "dataset":{"cells":grouped.get("nCells"),"subjects":grouped.get("nSubjects"),"genes":grouped.get("nGenes"),"externalM1Cells":ext.get("nExternalM1")},
      "evaluationDesign":{
        "broad":"18 traits; 5-fold grouped benchmarking reported in predictive_benchmark outputs",
        "strict":grouped.get("split"),
        "normalization":grouped.get("normalization"),
        "external":"VIS-trained frozen ExtraTrees evaluated in primary motor cortex",
        "negativeControls":"naive-vs-grouped split diagnostic + response permutation",
        "uncertainty":cal.get("method")
      },
      "findings":{
        "bestBroadModel":best_broad,
        "bestStrictModel":best_strict,
        "strongInternalTraits":strong_traits,
        "weakerInternalTraits":weak_traits,
        "externalMeanSpearman":ext_mean,
        "externalMeanAbsoluteSpearman":ext_abs_mean,
        "externalTopTraits":ext_top,
        "externalLowestTraits":ext_low,
        "meanCoverage90":cov90,
        "meanCoverage95":cov95,
        "meanSignalOverPermutationDelta":null_delta,
        "meanAbsoluteLeakageInflationDelta":leak_delta,
        "cbefWeightSensitivity":cbe_sens,
        "cbefCohortBootstrap":boot,
        "cbefPermutationControl":perm,
        "beamFactorExternalSummary":beam.get("externalSummary"),
        "evidenceTierCounts":tier_counts
      },
      "interpretation":{
        "accuracy":"ExtraTrees provides the strongest overall predictive accuracy among the current broad baselines, while PLS is the closest lower-complexity multivariate competitor.",
        "parsimony":"CBE Top-500 Ridge retains much of the predictive signal with fewer genes than all-gene linear models, supporting the usefulness of the evidence-ranked panel.",
        "generalization":"External M1 rank transfer is meaningful for several traits but uneven; positive Spearman with negative R2 on some targets indicates domain shift and calibration mismatch.",
        "robustness":"Grouped-vs-naive leakage deltas are small and permutation-null gaps are large, supporting real predictive signal under the tested design.",
        "integration":"CBEF rankings are stable to weighting and cohort bootstrap; BEAM-Factor does not materially improve external M1 mean Spearman over the raw bioelectric view, so multi-view integration should be treated as interpretive rather than as a demonstrated predictive gain."
      },
      "guardrails":[
        "Cross-paper metrics are contextual only unless datasets, preprocessing, targets and splits are matched.",
        "Mean MAE across heterogeneous electrophysiological units is not used as a global model-ranking metric.",
        "Negative external R2 with positive Spearman indicates rank transfer without reliable absolute-scale transfer.",
        "Engineering release checks and statistical benchmarks do not establish causal or clinical validity."
      ],
      "releaseIntegrity":{"passed":release.get("passed"),"total":release.get("total"),"publicationReadyEngineeringGate":release.get("publicationReady")}
    }
    (D/"comparative_benchmarking.json").write_text(json.dumps(benchmark,indent=2),encoding="utf-8")

    # Manuscript-ready report.
    report=[
      "# NEURO-BEAM Analytical and Comparative Benchmarking Report","",
      "## Benchmark design","",
      f"- Discovery benchmark: {grouped.get('nCells')} cells from {grouped.get('nSubjects')} subjects.",
      f"- Molecular predictors: {grouped.get('nGenes')} genes.",
      f"- Strict validation: {grouped.get('split')}.",
      f"- External validation: {ext.get('nExternalM1')} primary motor cortex cells.",
      "",
      "## Broad 18-trait model comparison","",
      mb.to_markdown(index=False),
      "",
      "## Strict grouped-CV model comparison","",
      strict_model.to_markdown(index=False),
      "",
      "## Key trait-level results","",
      f"- Strong internal ExtraTrees traits (Spearman >= 0.80): {', '.join(strong_traits) if strong_traits else 'none'}.",
      f"- Lower-signal internal traits (Spearman < 0.45): {', '.join(weak_traits) if weak_traits else 'none'}.",
      "",
      "## External M1 generalization","",
      ext_df.to_markdown(index=False),
      "",
      "## Calibration / uncertainty / controls","",
      f"- Mean 90% empirical coverage: {cov90:.3f}" if cov90 is not None else "- Mean 90% empirical coverage: NA",
      f"- Mean 95% empirical coverage: {cov95:.3f}" if cov95 is not None else "- Mean 95% empirical coverage: NA",
      f"- Mean signal-over-permutation Spearman delta: {null_delta:.3f}" if null_delta is not None else "- Permutation delta: NA",
      f"- Mean absolute naive-vs-grouped Spearman delta: {leak_delta:.4f}" if leak_delta is not None else "- Leakage delta: NA",
      "",
      "## CBEF / BEAM integration benchmarking","",
      f"- CBEF median rank Spearman across tested weights: {cbe_sens.get('medianRankSpearman')}.",
      f"- CBEF mean Top-50 cohort-bootstrap Jaccard: {boot.get('meanTop50Jaccard')}.",
      f"- CBEF permutation empirical p: {perm.get('empiricalP')}.",
      f"- BEAM-Factor external mean Spearman: raw={beam.get('externalSummary',{}).get('rawMeanSpearman')}, ephys factor={beam.get('externalSummary',{}).get('ephysFactorMeanSpearman')}, joint factor={beam.get('externalSummary',{}).get('jointFactorMeanSpearman')}.",
      "",
      "## Interpretation","",
      "- ExtraTrees is the strongest current predictive baseline overall.",
      "- PLS provides a competitive multivariate baseline using all genes.",
      "- The CBE Top-500 panel is informative and relatively parsimonious, but does not uniformly exceed nonlinear ExtraTrees.",
      "- External M1 transfer is trait-dependent; rank transfer is strongest for upstroke/downstroke ratio, rheobase, input resistance and membrane time constant among the compatible traits.",
      "- The multi-view cancer/ephys factorization is useful for structure discovery, but current external benchmarks do not show a predictive improvement over the raw bioelectric view.",
      "- Calibration, domain shift and evidence-class boundaries should remain visible in all manuscript claims.",
      "",
      "## Cross-literature context","",
      "Patch-seq studies have previously shown that gene expression can predict selected physiological phenotypes and that nonlinear or reduced-rank multimodal methods can capture cross-modal structure. Direct numerical ranking against those papers is not appropriate without matched cohorts, targets and split definitions; therefore NEURO-BEAM reports them as methodological context rather than head-to-head competitors."
    ]
    (DOC/"comparative_benchmarking_report.md").write_text("\n".join(report),encoding="utf-8")
    print(json.dumps({
      "bestBroad":best_broad["model"],
      "bestStrict":best_strict["model"],
      "externalMeanSpearman":ext_mean,
      "coverage90":cov90,
      "nullDelta":null_delta,
      "leakDelta":leak_delta
    },indent=2))

if __name__=="__main__": main()
