# NEURO-BEAM 3.0 — validated manuscript update

## New validation results incorporated into the manuscript

### Negative controls and leakage audit
Subject-grouped prediction was compared with naive random splitting and eight grouped permutation controls. Across the 11 principal electrophysiological traits, naive random splitting produced minimal performance inflation, whereas permuted targets yielded correlations close to zero. The mean real grouped-CV signal exceeded the permutation mean by approximately 0.665 Spearman units across traits. This indicates that the principal predictive signal is not explained by the evaluated subject-leakage or label-permutation controls.

### Predictive uncertainty and calibration
Subject-bootstrap confidence intervals were calculated for every principal trait. For ExtraTrees, examples include:
- upstroke/downstroke ratio: Spearman 0.909, 95% subject-bootstrap CI approximately 0.901–0.916;
- membrane time constant: 0.875, CI approximately 0.864–0.884;
- threshold current: 0.808, CI approximately 0.793–0.824;
- input resistance: 0.800, CI approximately 0.785–0.817.

Leave-one-fold-out residual intervals achieved approximately nominal 90% and 95% empirical coverage across the principal traits. Calibration slopes indicate that rank prediction is generally stronger than absolute calibration for several variables; this distinction is retained in all interpretation.

### Ranking robustness
The CBEF discovery ranking was assessed under alternative fusion rules, a broad weight grid, 300 cohort-bootstrap resamples and 1,000 cancer-evidence permutations. The median rank correlation across the weight grid was approximately 0.988, and mean Top-500 bootstrap Jaccard similarity was approximately 0.912. The observed Top-50 mean discovery score exceeded the permutation null with empirical p≈0.001. These analyses support robustness of broad membership while also demonstrating that the precise ordering of top genes depends on the evidence-fusion objective.

### Multi-objective Pareto evidence tiers
To avoid reliance on one composite score, NEURO-BEAM 3.0 assigns genes using five independent evidence axes:
1. bioelectric evidence;
2. cancer evidence;
3. bootstrap stability;
4. predictive-model importance;
5. external M1 replication.

Non-dominated sorting produces Pareto fronts without weighted fusion. Among the Top-500 genes, 25 currently meet Tier-A replicated criteria, 51 meet Tier-B robust criteria, and 424 remain Tier-C exploratory. Tier-A examples include CACNA2D3, DSCAM, GRIN3A, SLIT2, CEMIP, DOCK4 and CNTNAP4.

### Gene-level external replication
For 473 Top-500 genes represented in the independent M1 expression data, gene–electrical association fingerprints were evaluated over six semantically harmonized electrical traits. External replication scores combine direction concordance, cross-region association magnitude and electrical-fingerprint concordance. This layer is used for evidence-tier assignment and does not represent a perturbation experiment.

### Neurological-disease expansion
To reduce dependence on cancer-only disease context, NEURO-BEAM 3.0 adds an independent neurological-disease evidence layer from the Open Targets Platform. Association evidence is retained separately for Alzheimer disease, Parkinson disease, epilepsy, amyotrophic lateral sclerosis and stroke. Among the Top-500 discovery genes, 199 have at least one neurological-disease association in this layer. Examples include GRIN3A, SCN1A, SCN8A, CACNA1A, CACNA1C, KCNQ3 and KCND3.

The Open Targets score is never treated as mutation prevalence or electrophysiological effect size; it is displayed and analysed as a separate disease-evidence modality.

## Revised central manuscript claim
NEURO-BEAM is an explainable, leakage-aware, externally validated multi-evidence discovery framework that:
- learns neuronal bioelectric phenotype from matched Patch-seq data;
- quantifies uncertainty and negative-control performance;
- validates electrical associations in an independent cortical region;
- separates cancer somatic-genomic evidence from neurological target–disease evidence;
- prioritizes genes using both Pareto multi-objective analysis and transparent robustness criteria;
- converts association fingerprints into explicit, falsifiable membrane-dynamics hypotheses.

## Important negative findings retained
Two experimental modelling extensions are deliberately NOT promoted as primary novelty:
- CBEF-guided PLS priors provide only negligible predictive gain over the unweighted latent baseline;
- joint BEAM-Factor integration of cancer and bioelectric matrices does not improve mean external M1 association reproducibility over the electrophysiology-only factor model.

These negative results are retained as ablation evidence and support the decision to centre the manuscript on leakage-safe prediction, multi-objective evidence integration, external replication and transparent hypothesis generation rather than claiming improvement from cross-domain latent fusion alone.

## Current release status
The NEURO-BEAM 3.0 engineering/scientific-integrity audit passes 24 of 24 required checks. This status means that required artifacts, controls, validation outputs and evidence layers are present and internally auditable. It does not imply journal acceptance.
