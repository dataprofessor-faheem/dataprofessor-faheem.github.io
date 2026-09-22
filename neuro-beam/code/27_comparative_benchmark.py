"""NEURO-BEAM analytical and comparative benchmarking release."""
from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"data"

def paired_wilcoxon(a,b):
    a=np.asarray(a,float); b=np.asarray(b,float)
    mask=np.isfinite(a)&np.isfinite(b)
    a=a[mask]; b=b[mask]
    if len(a)<3: return {"n":int(len(a)),"stat":None,"p":None}
    d=a-b
    if np.allclose(d,0): return {"n":int(len(a)),"stat":0.0,"p":1.0}
    stat,p=wilcoxon(a,b,zero_method="wilcox",alternative="two-sided",method="auto")
    return {"n":int(len(a)),"stat":float(stat),"p":float(p)}

def mean_safe(x):
    x=pd.to_numeric(pd.Series(x),errors="coerce").dropna()
    return float(x.mean()) if len(x) else None

def main():
    grouped=pd.read_csv(D/"ml_grouped_cv_metrics_by_fold.csv")
    grouped_sum=pd.read_csv(D/"ml_grouped_cv_summary.csv")
    pred_sum=pd.read_csv(D/"predictive_benchmark_summary.csv")
    ext=pd.read_csv(D/"external_m1_validation.csv")
    m1=pd.read_csv(D/"m1_external_validation_metrics.csv")
    multitask=pd.read_csv(D/"cbef_multitask_trait_summary.csv")
    abl=pd.read_csv(D/"cbef_fusion_ablations.csv")
    neg=pd.read_csv(D/"ml_negative_control_summary.csv")
    cal=pd.read_csv(D/"ml_calibration_uncertainty.csv")
    beam=pd.read_csv(D/"beam_factor_cv.csv")

    # 1) paired fold-level ExtraTrees vs Ridge (valid grouped-CV benchmark)
    wide=grouped.pivot_table(index=["fold","target"],columns="model",values=["r2","mae","spearman"])
    pair_rows=[]
    for metric in ["spearman","r2","mae"]:
        et=wide[(metric,"ExtraTrees")]
        rg=wide[(metric,"Ridge")]
        w=paired_wilcoxon(et.values,rg.values)
        diff=(et-rg) if metric!="mae" else (rg-et)  # positive = ET better
        pair_rows.append({
            "comparison":"ExtraTrees vs Ridge",
            "metric":metric,
            "n_paired_fold_targets":w["n"],
            "extra_trees_mean":float(et.mean()),
            "ridge_mean":float(rg.mean()),
            "mean_advantage_et":float(diff.mean()),
            "median_advantage_et":float(diff.median()),
            "wilcoxon_stat":w["stat"],
            "p_value":w["p"],
            "direction_definition":"positive advantage favors ExtraTrees; for MAE advantage = Ridge MAE - ExtraTrees MAE"
        })
    pair=pd.DataFrame(pair_rows)
    pair.to_csv(D/"benchmark_pairwise_tests.csv",index=False)

    # 2) per-trait model table across broad internal models
    selected_models=["extra_trees_var400","pls_all","ridge_cbe_top500","ridge_all"]
    internal=pred_sum[pred_sum.model.isin(selected_models)].copy()
    pivot=internal.pivot_table(index="trait",columns="model",values=["mean_r2","mean_spearman","mean_mae"])
    trait_rows=[]
    for trait in sorted(internal.trait.unique()):
        sub=internal[internal.trait==trait].set_index("model")
        row={"trait":trait}
        for m in selected_models:
            if m in sub.index:
                row[f"{m}_r2"]=float(sub.loc[m,"mean_r2"])
                row[f"{m}_spearman"]=float(sub.loc[m,"mean_spearman"])
                row[f"{m}_mae"]=float(sub.loc[m,"mean_mae"])
        # best by spearman / r2
        ss=sub["mean_spearman"].astype(float)
        rr=sub["mean_r2"].astype(float)
        row["best_spearman_model"]=str(ss.idxmax())
        row["best_spearman"]=float(ss.max())
        row["best_r2_model"]=str(rr.idxmax())
        row["best_r2"]=float(rr.max())
        trait_rows.append(row)
    pd.DataFrame(trait_rows).to_csv(D/"benchmark_internal_trait_comparison.csv",index=False)

    model_summary=[]
    for m in selected_models:
        sub=internal[internal.model==m]
        model_summary.append({
            "model":m,
            "n_traits":int(len(sub)),
            "mean_r2":mean_safe(sub.mean_r2),
            "median_r2":float(sub.mean_r2.median()),
            "mean_spearman":mean_safe(sub.mean_spearman),
            "median_spearman":float(sub.mean_spearman.median()),
            "positive_r2_traits":int((sub.mean_r2>0).sum()),
            "spearman_ge_0_6_traits":int((sub.mean_spearman>=.6).sum())
        })
    model_summary_df=pd.DataFrame(model_summary)
    model_summary_df.to_csv(D/"benchmark_model_summary.csv",index=False)

    # 3) external feature-selection benchmark: Ridge all shared vs CBE Top500
    ext_w=ext.pivot_table(index="v1_trait",columns="model",values=["external_spearman","external_r2","external_mae_z"])
    ext_rows=[]
    if "ridge_shared_all" in ext_w["external_spearman"].columns and "ridge_cbe_top500" in ext_w["external_spearman"].columns:
        for metric in ["external_spearman","external_r2","external_mae_z"]:
            allv=ext_w[(metric,"ridge_shared_all")]
            top=ext_w[(metric,"ridge_cbe_top500")]
            if metric=="external_mae_z":
                advantage=allv-top
            else:
                advantage=top-allv
            w=paired_wilcoxon(top.values,allv.values) if metric!="external_mae_z" else paired_wilcoxon(allv.values,top.values)
            ext_rows.append({
                "comparison":"CBE Top500 Ridge vs all-shared-gene Ridge",
                "metric":metric,
                "n_traits":int(len(advantage)),
                "all_genes_mean":float(allv.mean()),
                "top500_mean":float(top.mean()),
                "mean_advantage_top500":float(advantage.mean()),
                "traits_improved_top500":int((advantage>0).sum()),
                "wilcoxon_stat":w["stat"],"p_value":w["p"]
            })
    pd.DataFrame(ext_rows).to_csv(D/"benchmark_external_feature_selection.csv",index=False)

    # 4) current frozen ET external metrics summary
    external_summary={
      "n_traits":int(len(m1)),
      "mean_spearman":float(m1.spearman.mean()),
      "median_spearman":float(m1.spearman.median()),
      "positive_spearman_traits":int((m1.spearman>0).sum()),
      "positive_r2_traits":int((m1.r2>0).sum()),
      "best_external_trait":str(m1.loc[m1.spearman.idxmax(),"target_vis"]),
      "best_external_spearman":float(m1.spearman.max())
    }

    # 5) negative control gap
    neg_grouped=neg[neg.experiment.str.startswith("grouped_permuted")].groupby("target").mean(numeric_only=True)
    et_sum=grouped_sum[grouped_sum.model=="ExtraTrees"].set_index("target")
    common=et_sum.index.intersection(neg_grouped.index)
    null_gap=(et_sum.loc[common,"spearman_mean"]-neg_grouped.loc[common,"mean_spearman"])
    negative_summary={
      "n_traits":int(len(common)),
      "mean_permuted_spearman":float(neg_grouped.loc[common,"mean_spearman"].mean()),
      "mean_real_spearman":float(et_sum.loc[common,"spearman_mean"].mean()),
      "mean_signal_over_permuted":float(null_gap.mean()),
      "min_signal_over_permuted":float(null_gap.min())
    }

    # 6) calibration summary
    cet=cal[cal.model=="ExtraTrees"]
    calibration_summary={
      "n_traits":int(len(cet)),
      "mean_abs_slope_deviation_from_1":float(np.mean(np.abs(cet.calibration_slope-1))),
      "median_abs_slope_deviation_from_1":float(np.median(np.abs(cet.calibration_slope-1))),
      "mean_abs_intercept":float(np.mean(np.abs(cet.calibration_intercept)))
    }

    # 7) CBEF multitask vs broad ET benchmark (descriptive: different architectures)
    mt=multitask[multitask.model=="latent_bioelectric_prior"]
    common_traits=sorted(set(mt.trait)&set(internal[internal.model=="extra_trees_var400"].trait))
    etb=internal[internal.model=="extra_trees_var400"].set_index("trait")
    mtb=mt.set_index("trait")
    mt_rows=[]
    for t in common_traits:
        mt_rows.append({
          "trait":t,
          "extra_trees_r2":float(etb.loc[t,"mean_r2"]),
          "multitask_r2":float(mtb.loc[t,"mean_r2"]),
          "delta_r2_multitask_minus_et":float(mtb.loc[t,"mean_r2"]-etb.loc[t,"mean_r2"]),
          "extra_trees_spearman":float(etb.loc[t,"mean_spearman"]),
          "multitask_spearman":float(mtb.loc[t,"mean_spearman"]),
          "delta_spearman_multitask_minus_et":float(mtb.loc[t,"mean_spearman"]-etb.loc[t,"mean_spearman"])
        })
    mt_df=pd.DataFrame(mt_rows)
    mt_df.to_csv(D/"benchmark_multitask_vs_baseline.csv",index=False)

    # 8) BEAM factor tradeoff summary
    beam_summary=[]
    for (rank,alpha),sub in beam.groupby(["rank","alpha"]):
        beam_summary.append({
          "rank":int(rank),"cancer_weight":float(alpha),
          "mean_ephys_rmse":float(sub.ephys_rmse.mean()),
          "mean_cancer_rmse":float(sub.cancer_rmse.mean()) if sub.cancer_rmse.notna().any() else None
        })
    pd.DataFrame(beam_summary).to_csv(D/"benchmark_beam_factor_tradeoff.csv",index=False)

    # 9) structured conclusions without ranking political-like concerns irrelevant; this is scientific.
    etrow=model_summary_df[model_summary_df.model=="extra_trees_var400"].iloc[0].to_dict()
    plsrow=model_summary_df[model_summary_df.model=="pls_all"].iloc[0].to_dict()
    ridge500=model_summary_df[model_summary_df.model=="ridge_cbe_top500"].iloc[0].to_dict()

    benchmark={
      "project":"NEURO-BEAM",
      "benchmarkVersion":"1.0",
      "benchmarkDesign":{
        "internal":"5-fold subject-grouped CV; fold-local preprocessing/feature selection",
        "external":"untouched primary motor cortex M1 cohort",
        "negativeControls":"grouped response permutations and naive-vs-grouped leakage diagnostic",
        "uncertainty":"subject bootstrap and cross-conformal coverage",
        "fusion":"CBEF ablations and BEAM-Factor ephys/cancer tradeoff"
      },
      "headline":{
        "extraTreesMeanSpearman18Traits":etrow["mean_spearman"],
        "extraTreesMeanR2_18Traits":etrow["mean_r2"],
        "plsMeanSpearman18Traits":plsrow["mean_spearman"],
        "cbeTop500RidgeMeanSpearman18Traits":ridge500["mean_spearman"],
        "externalFrozenET":external_summary,
        "negativeControls":negative_summary,
        "calibration":calibration_summary
      },
      "pairwiseFoldTests":pair_rows,
      "externalFeatureSelectionTests":ext_rows,
      "multitaskVsBaseline":{
        "nTraits":int(len(mt_df)),
        "meanDeltaR2":float(mt_df.delta_r2_multitask_minus_et.mean()),
        "meanDeltaSpearman":float(mt_df.delta_spearman_multitask_minus_et.mean()),
        "traitsMultitaskHigherR2":int((mt_df.delta_r2_multitask_minus_et>0).sum()),
        "traitsMultitaskHigherSpearman":int((mt_df.delta_spearman_multitask_minus_et>0).sum()),
        "interpretation":"Descriptive because the multitask prior and ExtraTrees baseline optimize different architectures/objectives."
      },
      "fusionAblations":abl.to_dict(orient="records"),
      "interpretation":{
        "strengths":[
          "Nonlinear ExtraTrees consistently improves subject-grouped prediction over Ridge across the measured electrical traits.",
          "Permutation controls are close to null while real grouped-CV signal is substantially positive.",
          "CBE Top500 feature selection improves external Ridge transfer on most compatible M1 traits compared with using all shared genes.",
          "Several electrical traits generalize in rank to M1, especially AP waveform ratio, rheobase, input resistance and membrane time constant."
        ],
        "limitations":[
          "External M1 absolute-scale R2 is negative for several traits, indicating substantial protocol/region/domain shift.",
          "Resting potential and threshold-voltage prediction remain comparatively weak.",
          "Multitask/cancer priors do not uniformly outperform the strongest nonlinear single-task baseline.",
          "BEAM-Factor cross-domain fusion introduces an ephys–cancer reconstruction tradeoff; joint structure should be interpreted as shared statistical structure, not causality."
        ]
      },
      "guardrail":"Benchmarking evaluates predictive/statistical performance in the available datasets. It does not establish clinical utility or causal biological mechanisms."
    }
    (D/"comparative_benchmark.json").write_text(json.dumps(benchmark,indent=2),encoding="utf-8")

    md=["# NEURO-BEAM Analytical and Comparative Benchmarking","",
        "## Benchmark design","",
        "- Internal: 5-fold subject-grouped CV with fold-local preprocessing.",
        "- External: untouched M1 Patch-seq cohort.",
        "- Robustness: permutation negative controls, calibration, uncertainty.",
        "- Cross-domain: CBEF ablations and BEAM-Factor tradeoff.","",
        "## Main analytical findings","",
        f'- ExtraTrees mean Spearman across 18-trait benchmark: **{etrow["mean_spearman"]:.3f}**; mean R²: **{etrow["mean_r2"]:.3f}**.',
        f'- PLS mean Spearman: **{plsrow["mean_spearman"]:.3f}**.',
        f'- CBE Top500 Ridge mean Spearman: **{ridge500["mean_spearman"]:.3f}**.',
        f'- Frozen ExtraTrees external M1 mean Spearman across {external_summary["n_traits"]} compatible traits: **{external_summary["mean_spearman"]:.3f}**.',
        f'- Mean real-vs-permuted grouped Spearman gap: **{negative_summary["mean_signal_over_permuted"]:.3f}**.',
        "",
        "## Interpretation","",
        "NEURO-BEAM is strongest for AP waveform ratio, membrane time constant, rheobase/threshold current and input resistance. External rank transfer is meaningful for several traits, while absolute calibration remains vulnerable to region/protocol domain shift.",
        "",
        "The cross-domain cancer/electrophysiology components add hypothesis-generation structure, but they do not uniformly improve pure electrophysiology prediction and should not be framed as causal evidence."
    ]
    (ROOT/"docs"/"comparative_benchmark_report.md").write_text("\n".join(md),encoding="utf-8")
    print(json.dumps({"models":len(model_summary_df),"pairwiseTests":len(pair),"externalFeatureSelectionTests":len(ext_rows)},indent=2))

if __name__=="__main__":
    main()
