# NMI Readiness Validation Matrix

| Requirement | Current status | Required next evidence |
|---|---|---|
| Novel ML/discovery method | CBEF v1 implemented | Benchmark against rank-fusion, CCA/PLS, learned fusion |
| Same-cell biological grounding | 3,654 Patch-seq cells | donor-aware mixed models; QC audit |
| External validation | M1 cohort reserved | frozen-feature replication and predictive validation |
| Top-500 discovery | workflow running | bootstrap stability and pathway enrichment |
| Cross-species mapping | automated ortholog mapping | manual audit of top-ranked genes |
| Predictive performance | partial | grouped donor CV; external test |
| Interpretability | score decomposition | SHAP/ablation/interaction analysis where applicable |
| Counterfactual modelling | normalized model implemented | sensitivity + negative controls; no causal language |
| Reproducibility | GitHub Actions + exports | versioned release; environment lock; tests |
| Broad utility | live portal | demonstrate 3-5 researcher use cases |
| Manuscript evidence | scaffold created | final results, figures, Methods, limitations |
| Journal fit | plausible | depends on model novelty + external validation strength |

## Minimum bar before submission
1. External M1 validation succeeds.
2. CBEF is compared against strong baseline fusion methods.
3. Ranking stability is quantified by bootstrap.
4. At least one predictive task shows meaningful generalization.
5. Every main claim has an explicit figure/table and source-data file.
6. Simulator claims remain explicitly counterfactual/hypothesis-generating.
7. Code release is deterministic from a clean checkout.
