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
- Mean 90% / 95% empirical uncertainty coverage: **0.900 / 0.949**.
- CBEF median rank Spearman across weight perturbations: **0.9881716787213799**.
- CBEF mean Top-50 cohort-bootstrap Jaccard: **0.8178053670892493**.
- CBEF permutation empirical p: **0.000999000999000999**.
- BEAM-Factor external mean Spearman (raw/ephys-factor/joint-factor): **0.39700641041118373 / 0.39703960933916016 / 0.39612546780307595**.
## Interpretation

NEURO-BEAM is strongest for AP waveform ratio, membrane time constant, rheobase/threshold current and input resistance. External rank transfer is meaningful for several traits, while absolute calibration remains vulnerable to region/protocol domain shift.

The cross-domain cancer/electrophysiology components add hypothesis-generation structure, but they do not uniformly improve pure electrophysiology prediction and should not be framed as causal evidence.