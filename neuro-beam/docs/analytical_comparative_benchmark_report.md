# NEURO-BEAM Analytical & Comparative Benchmarking Report

## Executive benchmark result

- Discovery/evaluation scale: **3654 cells**, **936 subjects**, **1302 genes**.
- Broad 18-trait model benchmark winner: **extra_trees_var400** (mean Spearman **0.612**, mean R² **0.341**).
- External M1 mean absolute Spearman across compatible traits: **0.417**.
- Mean signal-over-permutation delta: **0.665**.
- Mean empirical interval coverage: **0.900** (90% target), **0.949** (95% target).
- Replicated evidence core: **25 Tier-A** + **51 Tier-B** genes.
- Engineering/integrity gates: **24/24 passed**.

## Model benchmark

| benchmark_layer                    | model              |   n_traits |   n_genes |   mean_r2 |   median_r2 |   mean_spearman |   mean_mae |
|:-----------------------------------|:-------------------|-----------:|----------:|----------:|------------:|----------------:|-----------:|
| 18-trait internal model comparison | extra_trees_var400 |         18 |       400 |     0.341 |       0.269 |           0.612 |     16.989 |
| 18-trait internal model comparison | pls_all            |         18 |      1302 |     0.308 |       0.204 |           0.575 |     18.968 |
| 18-trait internal model comparison | ridge_cbe_top500   |         18 |       500 |     0.280 |       0.202 |           0.560 |     18.057 |
| 18-trait internal model comparison | ridge_all          |         18 |      1302 |     0.017 |      -0.055 |           0.476 |     21.062 |

## Grouped-CV benchmark

| model      |   n_traits |   mean_r2 |   median_r2 |   mean_spearman |   median_spearman |   mean_mae_unscaled |
|:-----------|-----------:|----------:|------------:|----------------:|------------------:|--------------------:|
| ExtraTrees |         11 |     0.387 |       0.287 |           0.672 |             0.678 |              10.413 |
| Ridge      |         11 |     0.100 |      -0.001 |           0.527 |             0.502 |              12.861 |

## Trait-level ExtraTrees vs Ridge

| trait                                 |   extratrees_r2 |   ridge_r2 |   extratrees_spearman |   ridge_spearman |   spearman_delta |   mae_relative_improvement_pct |
|:--------------------------------------|----------------:|-----------:|----------------------:|-----------------:|-----------------:|-------------------------------:|
| upstroke_downstroke_ratio_long_square |           0.732 |      0.716 |                 0.909 |            0.880 |            0.029 |                          5.791 |
| tau                                   |           0.613 |      0.486 |                 0.874 |            0.758 |            0.116 |                         21.369 |
| threshold_i_long_square               |           0.674 |      0.568 |                 0.808 |            0.735 |            0.074 |                         17.499 |
| ri                                    |           0.558 |      0.452 |                 0.799 |            0.726 |            0.073 |                         14.048 |
| adaptation                            |           0.211 |     -0.238 |                 0.708 |            0.404 |            0.304 |                         33.307 |
| avg_isi                               |           0.287 |     -0.001 |                 0.678 |            0.502 |            0.176 |                         28.762 |
| f_i_curve_slope                       |           0.540 |      0.329 |                 0.658 |            0.529 |            0.129 |                         22.581 |
| latency                               |           0.168 |     -0.512 |                 0.614 |            0.336 |            0.277 |                         41.357 |
| sag                                   |           0.226 |     -0.082 |                 0.584 |            0.455 |            0.129 |                         21.283 |
| threshold_v_long_square               |           0.142 |     -0.274 |                 0.433 |            0.269 |            0.165 |                         21.188 |
| vrest                                 |           0.111 |     -0.342 |                 0.325 |            0.199 |            0.126 |                         18.936 |

## External M1 benchmark

| target_vis                            |   spearman |      r2 |    mae | external_strength   |
|:--------------------------------------|-----------:|--------:|-------:|:--------------------|
| vrest                                 |      0.229 |  -0.550 |  8.577 | weak                |
| ri                                    |      0.556 |   0.120 | 78.709 | moderate            |
| tau                                   |      0.500 |   0.275 |  4.421 | moderate            |
| latency                               |      0.255 |  -0.492 | 71.429 | weak                |
| upstroke_downstroke_ratio_long_square |      0.627 |   0.195 |  0.913 | strong              |
| sag                                   |      0.327 | -95.164 |  1.040 | weak                |
| threshold_v_long_square               |      0.185 |  -0.029 |  5.667 | very weak           |
| threshold_i_long_square               |      0.612 |  -0.434 | 71.224 | strong              |
| adaptation                            |     -0.461 | -17.414 |  0.686 | moderate            |

## Robustness and uncertainty

- Mean grouped Spearman: 0.671
- Mean permuted Spearman: 0.006
- Mean signal-null delta: 0.665
- Max absolute naive/grouped split delta: 0.0085
- Mean 90% coverage: 0.900
- Mean 95% coverage: 0.949

## Multi-view benchmark

- Raw ephys/gene external mean Spearman: 0.397
- Ephys factor external mean Spearman: 0.397
- Joint ephys+cancer factor external mean Spearman: 0.396
- Joint minus raw: -0.0009

The lack of improvement from cancer-informed joint factorization is retained as a negative benchmark result; it argues against claiming that cancer context improves neuronal electrophysiology prediction.

## Evidence replication

- Genes evaluated in M1 replication: 473
- Tier A — replicated: 25
- Tier B — robust: 51
- Tier C — exploratory: 424

## Benchmark conclusions

1. **Nonlinear modelling improves internal prediction.** ExtraTrees is the best broad benchmark model (mean Spearman 0.612, mean R² 0.341).
2. **Predictability is strongly trait-dependent.** Best grouped-CV trait: upstroke_downstroke_ratio_long_square (Spearman 0.909, R² 0.732); weakest: vrest (Spearman 0.325).
3. **Several electrical phenotypes generalize across cortical regions, but not all.** Best external M1 |Spearman|: upstroke_downstroke_ratio_long_square=0.627; weakest: threshold_v_long_square=0.185; only 3/9 traits have positive external R².
4. **Permutation controls support genuine transcriptome–electrophysiology signal.** Mean grouped Spearman=0.671, mean permuted=0.006, mean signal-null delta=0.665.
5. **Subject grouping has little inflation relative to naive splitting in this dataset.** Mean naive-minus-grouped delta=-0.0001; max absolute delta=0.0085. Grouped splitting remains the valid design.
6. **Uncertainty coverage is well aligned with nominal targets.** Mean empirical coverage: 90% target=0.900; 95% target=0.949.
7. **Cancer-informed joint factorization does not improve external neuronal prediction.** Raw mean external Spearman=0.397; joint-factor=0.396; delta=-0.0009.
8. **Gene-level evidence includes an externally replicated core, not just discovery ranking.** 25 Tier-A replicated genes, 51 Tier-B robust genes; 473 genes evaluated in M1 replication.

## Interpretation guardrail

The composite maturity score is an internal descriptive scorecard, not a validated universal benchmark or ranking against other published projects. Cross-paper metrics are not treated as head-to-head unless datasets and endpoints are directly comparable.