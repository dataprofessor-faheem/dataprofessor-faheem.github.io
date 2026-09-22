# NEURO-BEAM Analytical and Comparative Benchmarking

## Benchmark design

- Internal: 5-fold subject-grouped CV with fold-local preprocessing.
- External: untouched M1 Patch-seq cohort.
- Robustness: permutation negative controls, calibration, uncertainty.
- Cross-domain: CBEF ablations and BEAM-Factor tradeoff.

## Main analytical findings

- ExtraTrees mean Spearman across 18-trait benchmark: **0.612**; mean R²: **0.341**.
- PLS mean Spearman: **0.575**.
- CBE Top500 Ridge mean Spearman: **0.560**.
- Frozen ExtraTrees external M1 mean Spearman across 9 compatible traits: **0.315**.
- Mean real-vs-permuted grouped Spearman gap: **0.666**.

## Interpretation

NEURO-BEAM is strongest for AP waveform ratio, membrane time constant, rheobase/threshold current and input resistance. External rank transfer is meaningful for several traits, while absolute calibration remains vulnerable to region/protocol domain shift.

The cross-domain cancer/electrophysiology components add hypothesis-generation structure, but they do not uniformly improve pure electrophysiology prediction and should not be framed as causal evidence.