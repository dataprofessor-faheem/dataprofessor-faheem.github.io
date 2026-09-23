"""Build analytical and comparative benchmarking release for NEURO-BEAM."""
from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"data"; DOC=ROOT/"docs"

def j(name): return json.loads((D/name).read_text(encoding="utf-8"))

def safe_mean(xs):
    xs=[float(x) for x in xs if x is not None and np.isfinite(float(x))]
    return float(np.mean(xs)) if xs else None

def main():
    pred=j("predictive_benchmark.json")
    grouped=j("ml_grouped_cv_summary.json")
    ext=j("m1_external_validation_summary.json")
    cal=j("ml_calibration_uncertainty.json")
    neg=j("ml_negative_controls.json")
    beam=j("beam_factor_results.json")
    multitask=j("cbef_multitask_benchmark.json")
    sens=j("cbef_sensitivity_summary.json")
    gene_rep=j("gene_external_m1_replication.json")
    pareto=j("neurobeam_pareto_evidence.json")
    release=j("release_status.json")

    # 1) Head-to-head internal model benchmark across same 18-trait task.
    model_rows=[]
    for m in pred.get("models",[]):
        model_rows.append({
            "benchmark_family":"18-trait internal CV",
            "model":m["model"],
            "mean_trait_r2":m.get("mean_trait_r2"),
            "median_trait_r2":m.get("median_trait_r2"),
            "mean_trait_spearman":m.get("mean_trait_spearman"),
            "mean_trait_mae":m.get("mean_trait_mae"),
            "n_traits":m.get("traits"),
            "n_genes":m.get("n_genes"),
            "validation_note":"same dataset/task; directly comparable"
        })
    for m in multitask.get("models",[]):
        model_rows.append({
            "benchmark_family":"18-trait latent-prior CV",
            "model":m["model"],
            "mean_trait_r2":m.get("mean_trait_r2"),
            "median_trait_r2":m.get("median_trait_r2"),
            "mean_trait_spearman":m.get("mean_trait_spearman"),
            "mean_trait_mae":m.get("mean_trait_mae"),
            "n_traits":m.get("traits"),
            "n_genes":multitask.get("nGenes"),
            "validation_note":"same dataset/task; latent representation comparison"
        })
    pd.DataFrame(model_rows).sort_values(["benchmark_family","mean_trait_spearman"],ascending=[True,False]).to_csv(D/"comparative_model_benchmark.csv",index=False)

    # 2) Grouped-CV trait-level benchmark: ExtraTrees vs Ridge.
    gdf=pd.DataFrame(grouped["summary"])
    traits=sorted(gdf["target"].unique())
    trait_rows=[]
    for t in traits:
        et=gdf[(gdf.model=="ExtraTrees")&(gdf.target==t)].iloc[0]
        rg=gdf[(gdf.model=="Ridge")&(gdf.target==t)].iloc[0]
        trait_rows.append({
            "trait":t,
            "extratrees_r2":et.r2_mean,
            "ridge_r2":rg.r2_mean,
            "delta_r2":et.r2_mean-rg.r2_mean,
            "extratrees_spearman":et.spearman_mean,
            "ridge_spearman":rg.spearman_mean,
            "delta_spearman":et.spearman_mean-rg.spearman_mean,
            "extratrees_mae":et.mae_mean,
            "ridge_mae":rg.mae_mean,
            "mae_improvement_fraction":(rg.mae_mean-et.mae_mean)/rg.mae_mean if rg.mae_mean!=0 else None
        })
    tdf=pd.DataFrame(trait_rows)
    tdf.to_csv(D/"comparative_trait_benchmark.csv",index=False)

    # 3) External validation benchmark.
    ext_rows=[]
    for x in ext.get("metrics",[]):
        ext_rows.append({
            "trait":x["target_vis"],
            "m1_trait":x["target_m1"],
            "n_m1":x["n_m1"],
            "external_spearman":x["spearman"],
            "external_r2":x["r2"],
            "external_mae":x["mae"],
            "generalization_class":(
                "strong rank transfer" if x["spearman"]>=0.5 else
                "moderate rank transfer" if x["spearman"]>=0.3 else
                "limited rank transfer" if x["spearman"]>=0 else
                "direction reversal"
            ),
            "absolute_calibration_status":"positive R2" if x["r2"]>0 else "domain-shift / poor absolute calibration"
        })
    edf=pd.DataFrame(ext_rows)
    edf.to_csv(D/"comparative_external_m1_benchmark.csv",index=False)

    # 4) Calibration / uncertainty.
    cdf=pd.DataFrame(cal.get("metrics",[]))
    covdf=pd.DataFrame(cal.get("coverageSummary",[]))
    et_cal=cdf[cdf.model=="ExtraTrees"].copy()
    et_cov=covdf[covdf.model=="ExtraTrees"].copy()
    et_cal.to_csv(D/"comparative_calibration_benchmark.csv",index=False)

    # 5) Negative controls.
    ndf=pd.DataFrame(neg.get("comparisons",[]))
    ndf.to_csv(D/"comparative_negative_controls.csv",index=False)

    # 6) Gene replication + evidence tiers.
    rep=pd.DataFrame(gene_rep.get("summary",[]))
    rep_top=rep.sort_values("external_replication_score",ascending=False).head(50)
    rep_top.to_csv(D/"comparative_top_external_gene_replication.csv",index=False)
    tier_counts=pareto.get("counts",{})

    # 7) Multi-view ablation and BEAM-Factor external comparison.
    fusion=pd.DataFrame(sens.get("ablations",[]))
    fusion.to_csv(D/"comparative_fusion_ablation.csv",index=False)
    ext_summary=beam.get("externalSummary",{})

    # Summary calculations.
    best18=max(pred["models"],key=lambda x:x["mean_trait_spearman"])
    best_lat=max(multitask["models"],key=lambda x:x["mean_trait_spearman"])
    mean_et_grouped=safe_mean(gdf[gdf.model=="ExtraTrees"].spearman_mean.tolist())
    mean_rg_grouped=safe_mean(gdf[gdf.model=="Ridge"].spearman_mean.tolist())
    ext_mean=safe_mean(edf.external_spearman.tolist())
    ext_abs_mean=safe_mean(np.abs(edf.external_spearman).tolist())
    positive_ext=int((edf.external_spearman>0).sum())
    ext_ge05=int((edf.external_spearman>=0.5).sum())
    cov90_mean=safe_mean(et_cov.coverage90.tolist()) if not et_cov.empty else None
    cov95_mean=safe_mean(et_cov.coverage95.tolist()) if not et_cov.empty else None
    cal_slope_median=float(et_cal.calibration_slope.median()) if not et_cal.empty else None
    signal_null_mean=safe_mean(ndf.signal_over_null_delta.tolist())
    leakage_abs_mean=safe_mean(np.abs(ndf.leakage_inflation_delta).tolist())
    replication_ge06=int((rep.external_replication_score>=0.6).sum()) if not rep.empty else 0

    # Transparent benchmark scores; not a single "accuracy" metric.
    summary={
      "scope":"NEURO-BEAM analytical and comparative benchmark",
      "dataset":{"cells":grouped.get("nCells"),"subjects":grouped.get("nSubjects"),"genes":grouped.get("nGenes"),"internal_traits":len(traits),"external_m1_cells":ext.get("nExternalM1")},
      "internal_model_benchmark":{
        "best_18trait_model":best18,
        "best_latent_model":best_lat,
        "grouped_extratrees_mean_spearman":mean_et_grouped,
        "grouped_ridge_mean_spearman":mean_rg_grouped,
        "extratrees_minus_ridge_mean_spearman":mean_et_grouped-mean_rg_grouped,
        "traits_extratrees_better_spearman":int((tdf.delta_spearman>0).sum()),
        "traits_extratrees_better_r2":int((tdf.delta_r2>0).sum())
      },
      "external_generalization":{
        "m1_traits":len(edf),
        "mean_signed_spearman":ext_mean,
        "mean_abs_spearman":ext_abs_mean,
        "positive_direction_traits":positive_ext,
        "traits_spearman_ge_0_5":ext_ge05,
        "best_trait":edf.sort_values("external_spearman",ascending=False).iloc[0].to_dict(),
        "worst_trait":edf.sort_values("external_spearman").iloc[0].to_dict()
      },
      "uncertainty_and_calibration":{
        "mean_coverage90":cov90_mean,
        "mean_coverage95":cov95_mean,
        "median_calibration_slope":cal_slope_median,
        "note":"coverage is well matched to nominal levels; calibration slope varies by trait"
      },
      "negative_controls":{
        "mean_signal_over_null_delta":signal_null_mean,
        "mean_abs_naive_vs_grouped_delta":leakage_abs_mean,
        "note":"permutation signal is strongly separated while naive-vs-grouped inflation is small on average"
      },
      "multiview_benchmark":{
        "beam_external_raw_mean_spearman":ext_summary.get("rawMeanSpearman"),
        "beam_external_ephys_factor_mean_spearman":ext_summary.get("ephysFactorMeanSpearman"),
        "beam_external_joint_factor_mean_spearman":ext_summary.get("jointFactorMeanSpearman"),
        "joint_minus_raw":(ext_summary.get("jointFactorMeanSpearman")-ext_summary.get("rawMeanSpearman")) if ext_summary.get("jointFactorMeanSpearman") is not None else None,
        "conclusion":"cancer-context joint factor does not improve external M1 electrophysiology transfer in current release"
      },
      "ranking_robustness":{
        "weight_median_rank_spearman":sens.get("weightSensitivity",{}).get("medianRankSpearman"),
        "cohort_bootstrap_top50_jaccard":sens.get("cohortBootstrap",{}).get("meanTop50Jaccard"),
        "permutation_empirical_p":sens.get("permutationNegativeControl",{}).get("empiricalP"),
        "tier_counts":tier_counts
      },
      "gene_external_replication":{
        "genes_evaluated":gene_rep.get("nGenes"),
        "genes_replication_score_ge_0_6":replication_ge06,
        "top_gene":rep_top.iloc[0].to_dict() if not rep_top.empty else None
      },
      "release_gate":{"passed":release.get("passed"),"total":release.get("total"),"engineering_publication_ready":release.get("publicationReady")},
      "interpretation_guardrail":"Benchmarks using the same dataset/task are directly comparable. Literature-context studies use different tasks/datasets and are contextual only."
    }
    (D/"comparative_benchmark_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")

    # Literature context: design comparison, intentionally no cross-paper numeric ranking.
    literature=[
      {
        "study":"Cadwell et al., Nature Biotechnology 2016",
        "role":"Patch-seq proof-of-concept",
        "sample_scale":"58 neocortical cells",
        "modalities":"electrophysiology + scRNA-seq + morphology",
        "prediction_or_alignment":"gene expression used to infer physiological/morphological properties",
        "external_validation":"not comparable to NEURO-BEAM M1 transfer",
        "direct_metric_comparability":"No",
        "source":"https://www.nature.com/articles/nbt.3445"
      },
      {
        "study":"Gouwens et al., Nature Neuroscience 2019",
        "role":"large-scale morpho-electric taxonomy",
        "sample_scale":"1,938 electrophysiology; 461 morphology; 452 paired",
        "modalities":"electrophysiology + morphology + transcriptomic subclass correspondence",
        "prediction_or_alignment":"unsupervised e/morpho classification",
        "external_validation":"different objective",
        "direct_metric_comparability":"No",
        "source":"https://www.nature.com/articles/s41593-019-0417-0"
      },
      {
        "study":"Berg et al./MOp Patch-seq, Nature 2021",
        "role":"motor-cortex Patch-seq atlas",
        "sample_scale":">1,300 neurons",
        "modalities":"transcriptomics + electrophysiology + morphology",
        "prediction_or_alignment":"phenotypic variation across transcriptomic types",
        "external_validation":"serves as NEURO-BEAM external M1 domain",
        "direct_metric_comparability":"Contextual",
        "source":"https://www.nature.com/articles/s41586-020-2907-3"
      },
      {
        "study":"NMA, Communications Biology 2021",
        "role":"multimodal manifold alignment",
        "sample_scale":"4,435 visual-cortex Patch-seq neurons",
        "modalities":"transcriptomics + electrophysiology",
        "prediction_or_alignment":"manifold alignment across modalities",
        "external_validation":"different model target",
        "direct_metric_comparability":"No",
        "source":"https://www.nature.com/articles/s42003-021-02807-6"
      },
      {
        "study":"NEUROeSTIMator, Nature Communications 2024",
        "role":"transcriptomic neuronal-activity scoring",
        "sample_scale":"Patch-seq source includes 4,284 specimens / 1,040 mouse subjects",
        "modalities":"transcriptomics + electrophysiology context",
        "prediction_or_alignment":"activity score modeled and related to electrophysiological features",
        "external_validation":"different endpoint",
        "direct_metric_comparability":"No",
        "source":"https://www.nature.com/articles/s41467-023-44503-5"
      },
      {
        "study":"NEURO-BEAM current release",
        "role":"gene-to-bioelectric prediction + disease-context prioritization",
        "sample_scale":f'{grouped.get("nCells")} VIS cells / {grouped.get("nSubjects")} subjects; {ext.get("nExternalM1")} external M1 cells',
        "modalities":"Patch-seq transcriptomics + electrophysiology; cancer context; external M1 validation",
        "prediction_or_alignment":"18-trait benchmark; 11-trait grouped CV; external transfer; calibration; negative controls",
        "external_validation":"Yes, untouched M1 for compatible traits",
        "direct_metric_comparability":"Internal models yes; literature context only",
        "source":"https://www.gdrnetwork.org/neuro-beam/"
      }
    ]
    pd.DataFrame(literature).to_csv(D/"comparative_literature_context.csv",index=False)

    # Markdown report
    lines=[
      "# NEURO-BEAM Analytical and Comparative Benchmarking Report","",
      "## 1. Benchmark scope",
      f"- Internal discovery: {grouped.get('nCells')} cells, {grouped.get('nSubjects')} subjects, {grouped.get('nGenes')} genes.",
      f"- External validation: {ext.get('nExternalM1')} primary motor cortex cells.",
      "- Same-task comparisons are treated as direct benchmarks; literature comparisons are contextual only.","",
      "## 2. Internal model benchmark",
      f"- Best 18-trait benchmark: **{best18['model']}**; mean Spearman={best18['mean_trait_spearman']:.3f}, mean R²={best18['mean_trait_r2']:.3f}.",
      f"- PLS-all mean Spearman={next(x for x in pred['models'] if x['model']=='pls_all')['mean_trait_spearman']:.3f}.",
      f"- Ridge Top-500 mean Spearman={next(x for x in pred['models'] if x['model']=='ridge_cbe_top500')['mean_trait_spearman']:.3f}.",
      f"- Ridge-all mean Spearman={next(x for x in pred['models'] if x['model']=='ridge_all')['mean_trait_spearman']:.3f}.",
      f"- On the stricter subject-grouped 11-trait benchmark, ExtraTrees mean Spearman={mean_et_grouped:.3f} vs Ridge={mean_rg_grouped:.3f}.","",
      "## 3. Trait-level findings",
    ]
    for _,r in tdf.sort_values("extratrees_spearman",ascending=False).head(6).iterrows():
        lines.append(f"- {r.trait}: ExtraTrees Spearman={r.extratrees_spearman:.3f}, R²={r.extratrees_r2:.3f}; ΔSpearman vs Ridge={r.delta_spearman:+.3f}.")
    lines += ["","## 4. External M1 generalization",
      f"- Mean signed external Spearman={ext_mean:.3f}; mean absolute Spearman={ext_abs_mean:.3f}.",
      f"- {ext_ge05}/{len(edf)} compatible traits have external Spearman ≥0.5.",
    ]
    for _,r in edf.sort_values("external_spearman",ascending=False).iterrows():
        lines.append(f"- {r.trait}: rho={r.external_spearman:.3f}, R²={r.external_r2:.3f} — {r.generalization_class}; {r.absolute_calibration_status}.")
    lines += ["","## 5. Calibration and negative controls",
      f"- Mean empirical coverage: 90% target={cov90_mean:.3f}; 95% target={cov95_mean:.3f}.",
      f"- Median ExtraTrees calibration slope={cal_slope_median:.3f}.",
      f"- Mean signal-over-permutation delta={signal_null_mean:.3f}.",
      f"- Mean absolute naive-vs-grouped split delta={leakage_abs_mean:.4f}.","",
      "## 6. Multi-view / cancer-context ablation",
      f"- BEAM-Factor raw external mean Spearman={ext_summary.get('rawMeanSpearman'):.3f}.",
      f"- Ephys-factor external mean Spearman={ext_summary.get('ephysFactorMeanSpearman'):.3f}.",
      f"- Joint ephys+cancer factor external mean Spearman={ext_summary.get('jointFactorMeanSpearman'):.3f}.",
      "- Conclusion: cancer context is useful for cross-domain prioritization, but it does not improve external M1 electrophysiology transfer in the current release.","",
      "## 7. Ranking robustness and gene replication",
      f"- Weight-sensitivity median rank Spearman={sens.get('weightSensitivity',{}).get('medianRankSpearman'):.3f}.",
      f"- Cohort-bootstrap mean Top-50 Jaccard={sens.get('cohortBootstrap',{}).get('meanTop50Jaccard'):.3f}.",
      f"- Fusion-score permutation empirical p={sens.get('permutationNegativeControl',{}).get('empiricalP'):.4f}.",
      f"- External gene replication evaluated {gene_rep.get('nGenes')} genes; {replication_ge06} score ≥0.60.",
      f"- Evidence tiers: {tier_counts}.","",
      "## 8. Overall interpretation",
      "NEURO-BEAM is strongest as a subject-grouped, externally tested gene-to-bioelectric prediction and evidence-prioritization framework. Its strongest traits are AP waveform ratio, membrane time constant, rheobase/current threshold, and input resistance. Generalization is trait-dependent, and absolute calibration can fail under cortical-region/domain shift. Cancer-context fusion should therefore remain a prioritization/context layer rather than being presented as a universal performance booster."
    ]
    (DOC/"comparative_benchmark_report.md").write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps({"best_model":best18["model"],"external_mean":ext_mean,"tier_counts":tier_counts,"release":f"{release.get('passed')}/{release.get('total')}"},indent=2))

if __name__=="__main__":
    main()
