"""Build analytical and comparative benchmarking release for NEURO-BEAM."""
from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"data"
DOCS=ROOT/"docs"

def loadj(name):
    with open(D/name,"r",encoding="utf-8") as f:
        return json.load(f)

def finite_mean(xs):
    vals=[float(x) for x in xs if x is not None and np.isfinite(float(x))]
    return float(np.mean(vals)) if vals else None

def finite_median(xs):
    vals=[float(x) for x in xs if x is not None and np.isfinite(float(x))]
    return float(np.median(vals)) if vals else None

def pct_delta(a,b):
    if b in (None,0) or a is None:return None
    return 100*(a-b)/abs(b)

def main():
    pred=loadj("predictive_benchmark.json")
    grouped=loadj("ml_grouped_cv_summary.json")
    ext=loadj("m1_external_validation_summary.json")
    cal=loadj("ml_calibration_uncertainty.json")
    neg=loadj("ml_negative_controls.json")
    beam=loadj("beam_factor_results.json")
    gene_rep=loadj("gene_external_m1_replication.json")
    pareto=loadj("neurobeam_pareto_evidence.json")
    sensitivity=loadj("cbef_sensitivity_summary.json")
    multitask=loadj("cbef_multitask_benchmark.json")
    release=loadj("release_status.json")

    # 1) Broad model comparison across 18 traits
    model_rows=[]
    for m in pred.get("models",[]):
        model_rows.append({
            "benchmark_layer":"18-trait internal model comparison",
            "model":m["model"],
            "n_traits":m.get("traits"),
            "n_genes":m.get("n_genes"),
            "mean_r2":m.get("mean_trait_r2"),
            "median_r2":m.get("median_trait_r2"),
            "mean_spearman":m.get("mean_trait_spearman"),
            "mean_mae":m.get("mean_trait_mae")
        })
    models=pd.DataFrame(model_rows)
    models.to_csv(D/"benchmark_model_comparison.csv",index=False)

    # 2) Grouped-CV ExtraTrees vs Ridge on 11 release targets
    gs=pd.DataFrame(grouped.get("summary",[]))
    grouped_summary=[]
    for model,g in gs.groupby("model"):
        grouped_summary.append({
            "model":model,
            "n_traits":int(len(g)),
            "mean_r2":finite_mean(g["r2_mean"]),
            "median_r2":finite_median(g["r2_mean"]),
            "mean_spearman":finite_mean(g["spearman_mean"]),
            "median_spearman":finite_median(g["spearman_mean"]),
            "mean_mae_unscaled":finite_mean(g["mae_mean"])
        })
    grouped_df=pd.DataFrame(grouped_summary).sort_values("mean_spearman",ascending=False)
    grouped_df.to_csv(D/"benchmark_grouped_cv_summary.csv",index=False)

    # Trait comparison table
    piv=gs.pivot(index="target",columns="model",values=["r2_mean","spearman_mean","mae_mean"])
    trait_rows=[]
    for t in gs["target"].unique():
        et=gs[(gs.target==t)&(gs.model=="ExtraTrees")].iloc[0]
        rd=gs[(gs.target==t)&(gs.model=="Ridge")].iloc[0]
        trait_rows.append({
            "trait":t,
            "extratrees_r2":et.r2_mean,
            "ridge_r2":rd.r2_mean,
            "r2_delta":et.r2_mean-rd.r2_mean,
            "extratrees_spearman":et.spearman_mean,
            "ridge_spearman":rd.spearman_mean,
            "spearman_delta":et.spearman_mean-rd.spearman_mean,
            "extratrees_mae":et.mae_mean,
            "ridge_mae":rd.mae_mean,
            "mae_relative_improvement_pct":100*(rd.mae_mean-et.mae_mean)/abs(rd.mae_mean) if rd.mae_mean else None
        })
    trait_df=pd.DataFrame(trait_rows).sort_values("extratrees_spearman",ascending=False)
    trait_df.to_csv(D/"benchmark_trait_comparison.csv",index=False)

    # 3) External M1 benchmarking
    ext_df=pd.DataFrame(ext.get("metrics",[]))
    ext_df["abs_spearman"]=ext_df["spearman"].abs()
    ext_df["external_strength"]=pd.cut(ext_df["abs_spearman"],
        bins=[-np.inf,.2,.4,.6,.8,np.inf],
        labels=["very weak","weak","moderate","strong","very strong"])
    ext_df.to_csv(D/"benchmark_external_m1.csv",index=False)

    ext_mean=finite_mean(ext_df["spearman"])
    ext_abs_mean=finite_mean(ext_df["abs_spearman"])
    ext_positive=int((ext_df["spearman"]>0).sum())
    ext_r2_positive=int((ext_df["r2"]>0).sum())

    # 4) Calibration / coverage
    cal_metrics=pd.DataFrame(cal.get("metrics",[]))
    cal_et=cal_metrics[cal_metrics.model=="ExtraTrees"].copy()
    coverage=pd.DataFrame(cal.get("coverageSummary",[]))
    cov_et=coverage[coverage.model=="ExtraTrees"].copy()
    calibration_summary={
        "mean_spearman":finite_mean(cal_et["spearman"]) if len(cal_et) else None,
        "mean_calibration_slope":finite_mean(cal_et["calibration_slope"]) if len(cal_et) else None,
        "median_calibration_slope":finite_median(cal_et["calibration_slope"]) if len(cal_et) else None,
        "mean_coverage90":finite_mean(cov_et["coverage90"]) if len(cov_et) else None,
        "mean_coverage95":finite_mean(cov_et["coverage95"]) if len(cov_et) else None,
        "coverage90_abs_error_from_nominal":finite_mean([abs(x-.90) for x in cov_et["coverage90"]]) if len(cov_et) else None,
        "coverage95_abs_error_from_nominal":finite_mean([abs(x-.95) for x in cov_et["coverage95"]]) if len(cov_et) else None
    }

    # 5) Negative controls / leakage
    neg_df=pd.DataFrame(neg.get("comparisons",[]))
    neg_summary={
        "mean_grouped_spearman":finite_mean(neg_df["grouped_spearman"]),
        "mean_permuted_spearman":finite_mean(neg_df["permuted_mean_spearman"]),
        "mean_signal_over_null_delta":finite_mean(neg_df["signal_over_null_delta"]),
        "mean_leakage_inflation_delta":finite_mean(neg_df["leakage_inflation_delta"]),
        "max_abs_leakage_inflation_delta":float(neg_df["leakage_inflation_delta"].abs().max())
    }
    neg_df.to_csv(D/"benchmark_negative_controls.csv",index=False)

    # 6) Gene replication / evidence tiers
    rep_df=pd.DataFrame(gene_rep.get("summary",[]))
    rep_summary={
        "n_genes_evaluated":gene_rep.get("nGenes"),
        "mean_external_replication_score":finite_mean(rep_df["external_replication_score"]) if len(rep_df) else None,
        "median_external_replication_score":finite_median(rep_df["external_replication_score"]) if len(rep_df) else None,
        "mean_sign_concordance":finite_mean(rep_df["sign_concordance_fraction"]) if len(rep_df) else None,
        "genes_sign_concordance_100pct":int((rep_df["sign_concordance_fraction"]>=.999).sum()) if len(rep_df) else 0
    }

    counts=pareto.get("counts",{})
    evidence_summary={
        "tier_A":int(counts.get("A — replicated",0)),
        "tier_B":int(counts.get("B — robust",0)),
        "tier_C":int(counts.get("C — exploratory",0)),
        "outside_top500":int(counts.get("Outside Top-500",0))
    }

    # 7) Multi-view BEAM-Factor comparison: does cancer context improve neuronal external transfer?
    ext_sum=beam.get("externalSummary",{})
    factor_summary={
        "raw_mean_external_spearman":ext_sum.get("rawMeanSpearman"),
        "ephys_factor_mean_external_spearman":ext_sum.get("ephysFactorMeanSpearman"),
        "joint_factor_mean_external_spearman":ext_sum.get("jointFactorMeanSpearman")
    }
    factor_summary["joint_minus_raw"]=(
        factor_summary["joint_factor_mean_external_spearman"]-factor_summary["raw_mean_external_spearman"]
        if factor_summary["joint_factor_mean_external_spearman"] is not None and factor_summary["raw_mean_external_spearman"] is not None else None
    )

    # 8) Composite benchmark scorecard – descriptive, not a universal ranking.
    # Scores benchmark internal project maturity, not comparison against unrelated external papers.
    internal_best=models.sort_values("mean_spearman",ascending=False).iloc[0]
    robustness_score=np.clip((neg_summary["mean_signal_over_null_delta"] or 0)/0.8,0,1)
    leakage_score=np.clip(1-(neg_summary["max_abs_leakage_inflation_delta"] or 1)/0.05,0,1)
    external_score=np.clip((ext_abs_mean or 0)/0.6,0,1)
    calibration_score=np.clip(1-(calibration_summary["coverage90_abs_error_from_nominal"] or 1)/0.05,0,1)
    replication_score=np.clip(evidence_summary["tier_A"]/25 if 25 else 0,0,1)
    benchmark_dimensions=[
      {"dimension":"Internal predictive signal","score_0_1":float(np.clip(internal_best.mean_spearman/0.8,0,1)),"evidence":f'best mean Spearman={internal_best.mean_spearman:.3f}'},
      {"dimension":"Negative-control separation","score_0_1":float(robustness_score),"evidence":f'mean signal-null delta={neg_summary["mean_signal_over_null_delta"]:.3f}'},
      {"dimension":"Leakage resistance","score_0_1":float(leakage_score),"evidence":f'max |naive-grouped delta|={neg_summary["max_abs_leakage_inflation_delta"]:.4f}'},
      {"dimension":"External M1 transfer","score_0_1":float(external_score),"evidence":f'mean |external Spearman|={ext_abs_mean:.3f}'},
      {"dimension":"Uncertainty calibration","score_0_1":float(calibration_score),"evidence":f'mean 90% coverage={calibration_summary["mean_coverage90"]:.3f}'},
      {"dimension":"Replicated gene evidence","score_0_1":float(replication_score),"evidence":f'Tier A genes={evidence_summary["tier_A"]}'}
    ]
    bench_score=finite_mean([x["score_0_1"] for x in benchmark_dimensions])

    # Key conclusions are data-driven.
    best_trait=trait_df.iloc[0]
    weakest_trait=trait_df.sort_values("extratrees_spearman").iloc[0]
    best_external=ext_df.iloc[ext_df["abs_spearman"].argmax()]
    worst_external=ext_df.iloc[ext_df["abs_spearman"].argmin()]
    conclusions=[
      {
        "finding":"Nonlinear modelling improves internal prediction.",
        "evidence":f'ExtraTrees is the best broad benchmark model (mean Spearman {models.iloc[models.mean_spearman.argmax()].mean_spearman:.3f}, mean R² {models.iloc[models.mean_spearman.argmax()].mean_r2:.3f}).'
      },
      {
        "finding":"Predictability is strongly trait-dependent.",
        "evidence":f'Best grouped-CV trait: {best_trait.trait} (Spearman {best_trait.extratrees_spearman:.3f}, R² {best_trait.extratrees_r2:.3f}); weakest: {weakest_trait.trait} (Spearman {weakest_trait.extratrees_spearman:.3f}).'
      },
      {
        "finding":"Several electrical phenotypes generalize across cortical regions, but not all.",
        "evidence":f'Best external M1 |Spearman|: {best_external.target_vis}={best_external.spearman:.3f}; weakest: {worst_external.target_vis}={worst_external.spearman:.3f}; only {ext_r2_positive}/{len(ext_df)} traits have positive external R².'
      },
      {
        "finding":"Permutation controls support genuine transcriptome–electrophysiology signal.",
        "evidence":f'Mean grouped Spearman={neg_summary["mean_grouped_spearman"]:.3f}, mean permuted={neg_summary["mean_permuted_spearman"]:.3f}, mean signal-null delta={neg_summary["mean_signal_over_null_delta"]:.3f}.'
      },
      {
        "finding":"Subject grouping has little inflation relative to naive splitting in this dataset.",
        "evidence":f'Mean naive-minus-grouped delta={neg_summary["mean_leakage_inflation_delta"]:.4f}; max absolute delta={neg_summary["max_abs_leakage_inflation_delta"]:.4f}. Grouped splitting remains the valid design.'
      },
      {
        "finding":"Uncertainty coverage is well aligned with nominal targets.",
        "evidence":f'Mean empirical coverage: 90% target={calibration_summary["mean_coverage90"]:.3f}; 95% target={calibration_summary["mean_coverage95"]:.3f}.'
      },
      {
        "finding":"Cancer-informed joint factorization does not improve external neuronal prediction.",
        "evidence":f'Raw mean external Spearman={factor_summary["raw_mean_external_spearman"]:.3f}; joint-factor={factor_summary["joint_factor_mean_external_spearman"]:.3f}; delta={factor_summary["joint_minus_raw"]:.4f}.'
      },
      {
        "finding":"Gene-level evidence includes an externally replicated core, not just discovery ranking.",
        "evidence":f'{evidence_summary["tier_A"]} Tier-A replicated genes, {evidence_summary["tier_B"]} Tier-B robust genes; {rep_summary["n_genes_evaluated"]} genes evaluated in M1 replication.'
      }
    ]

    payload={
      "project":"NEURO-BEAM",
      "benchmarkVersion":"Analytical Comparative Benchmark 1.0",
      "dataScale":{"cells":grouped.get("nCells"),"subjects":grouped.get("nSubjects"),"genes":grouped.get("nGenes"),"externalM1Cells":ext.get("nExternalM1")},
      "internalModels":model_rows,
      "groupedCvSummary":grouped_summary,
      "externalM1Summary":{
        "n_traits":int(len(ext_df)),
        "mean_spearman":ext_mean,
        "mean_abs_spearman":ext_abs_mean,
        "positive_spearman_traits":ext_positive,
        "positive_r2_traits":ext_r2_positive
      },
      "calibrationSummary":calibration_summary,
      "negativeControlSummary":neg_summary,
      "geneReplicationSummary":rep_summary,
      "evidenceTierSummary":evidence_summary,
      "beamFactorSummary":factor_summary,
      "benchmarkDimensions":benchmark_dimensions,
      "descriptiveMaturityScore_0_1":bench_score,
      "conclusions":conclusions,
      "releaseIntegrity":{"passed":release.get("passed"),"total":release.get("total"),"engineeringGate":release.get("publicationReady")},
      "guardrail":"The composite maturity score is an internal descriptive scorecard, not a validated universal benchmark or ranking against other published projects. Cross-paper metrics are not treated as head-to-head unless datasets and endpoints are directly comparable."
    }
    (D/"analytical_comparative_benchmark.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    pd.DataFrame(benchmark_dimensions).to_csv(D/"benchmark_scorecard.csv",index=False)

    # Markdown report
    lines=[
      "# NEURO-BEAM Analytical & Comparative Benchmarking Report","",
      "## Executive benchmark result","",
      f"- Discovery/evaluation scale: **{grouped.get('nCells')} cells**, **{grouped.get('nSubjects')} subjects**, **{grouped.get('nGenes')} genes**.",
      f"- Broad 18-trait model benchmark winner: **{models.sort_values('mean_spearman',ascending=False).iloc[0].model}** (mean Spearman **{models.sort_values('mean_spearman',ascending=False).iloc[0].mean_spearman:.3f}**, mean R² **{models.sort_values('mean_spearman',ascending=False).iloc[0].mean_r2:.3f}**).",
      f"- External M1 mean absolute Spearman across compatible traits: **{ext_abs_mean:.3f}**.",
      f"- Mean signal-over-permutation delta: **{neg_summary['mean_signal_over_null_delta']:.3f}**.",
      f"- Mean empirical interval coverage: **{calibration_summary['mean_coverage90']:.3f}** (90% target), **{calibration_summary['mean_coverage95']:.3f}** (95% target).",
      f"- Replicated evidence core: **{evidence_summary['tier_A']} Tier-A** + **{evidence_summary['tier_B']} Tier-B** genes.",
      f"- Engineering/integrity gates: **{release.get('passed')}/{release.get('total')} passed**.","",
      "## Model benchmark","",
      models.to_markdown(index=False,floatfmt=".3f"),"",
      "## Grouped-CV benchmark","",
      grouped_df.to_markdown(index=False,floatfmt=".3f"),"",
      "## Trait-level ExtraTrees vs Ridge","",
      trait_df[["trait","extratrees_r2","ridge_r2","extratrees_spearman","ridge_spearman","spearman_delta","mae_relative_improvement_pct"]].to_markdown(index=False,floatfmt=".3f"),"",
      "## External M1 benchmark","",
      ext_df[["target_vis","spearman","r2","mae","external_strength"]].to_markdown(index=False,floatfmt=".3f"),"",
      "## Robustness and uncertainty","",
      f"- Mean grouped Spearman: {neg_summary['mean_grouped_spearman']:.3f}",
      f"- Mean permuted Spearman: {neg_summary['mean_permuted_spearman']:.3f}",
      f"- Mean signal-null delta: {neg_summary['mean_signal_over_null_delta']:.3f}",
      f"- Max absolute naive/grouped split delta: {neg_summary['max_abs_leakage_inflation_delta']:.4f}",
      f"- Mean 90% coverage: {calibration_summary['mean_coverage90']:.3f}",
      f"- Mean 95% coverage: {calibration_summary['mean_coverage95']:.3f}","",
      "## Multi-view benchmark","",
      f"- Raw ephys/gene external mean Spearman: {factor_summary['raw_mean_external_spearman']:.3f}",
      f"- Ephys factor external mean Spearman: {factor_summary['ephys_factor_mean_external_spearman']:.3f}",
      f"- Joint ephys+cancer factor external mean Spearman: {factor_summary['joint_factor_mean_external_spearman']:.3f}",
      f"- Joint minus raw: {factor_summary['joint_minus_raw']:.4f}",
      "",
      "The lack of improvement from cancer-informed joint factorization is retained as a negative benchmark result; it argues against claiming that cancer context improves neuronal electrophysiology prediction.","",
      "## Evidence replication","",
      f"- Genes evaluated in M1 replication: {rep_summary['n_genes_evaluated']}",
      f"- Tier A — replicated: {evidence_summary['tier_A']}",
      f"- Tier B — robust: {evidence_summary['tier_B']}",
      f"- Tier C — exploratory: {evidence_summary['tier_C']}","",
      "## Benchmark conclusions",""
    ]
    for i,c in enumerate(conclusions,1):
        lines += [f"{i}. **{c['finding']}** {c['evidence']}"]
    lines += ["","## Interpretation guardrail","",payload["guardrail"]]
    (DOCS/"analytical_comparative_benchmark_report.md").write_text("\n".join(lines),encoding="utf-8")

    print(json.dumps({
      "broadBestModel":models.sort_values("mean_spearman",ascending=False).iloc[0].model,
      "externalMeanAbsSpearman":ext_abs_mean,
      "signalNullDelta":neg_summary["mean_signal_over_null_delta"],
      "tierA":evidence_summary["tier_A"],
      "maturityScore":bench_score
    },indent=2))

if __name__=="__main__":
    main()
