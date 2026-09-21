# Nature Machine Intelligence–oriented Manuscript Blueprint

## Working title
**NEURO-BEAM: Explainable Machine Intelligence Links Neuronal Bioelectric Phenotypes to Cross-Disease Genomic Programs**

Alternative:
**A multimodal machine-intelligence atlas connects neuronal electrophysiology, transcriptomic regulation and pan-cancer genomic alteration**

## Central scientific question
Can a machine-intelligence framework discover reproducible molecular programs associated with neuronal bioelectric phenotypes and use those programs to generate interpretable cross-disease genomic hypotheses without conflating unmatched data sources?

## Primary contribution
NEURO-BEAM is not presented as a website. The contribution is an explainable computational framework that:
1. learns bioelectric phenotypes from electrophysiology;
2. identifies same-cell transcriptomic associations;
3. separates cell-identity effects from electrical-state effects;
4. transfers the molecular signatures into independent disease-genomics cohorts;
5. quantifies uncertainty, robustness and cross-cohort reproducibility;
6. provides interactive, reproducible exploration and phenotype-constrained dynamic simulation.

## Core novelty claims to test
### N1 — Bioelectric representation
A low-dimensional bioelectric representation captures stable neuronal phenotypes beyond broad inhibitory subtype labels.

### N2 — Molecular predictability
Transcriptomic features predict electrical phenotypes under subject-grouped validation.

### N3 — Interpretable gene programs
Stable gene modules and individual genes associate with electrical traits after FDR control and within-class sensitivity analysis.

### N4 — Cross-domain disease projection
Disease genomic alterations can be projected onto empirically learned bioelectric-associated gene programs to create reproducible hypothesis-prioritization signatures.

### N5 — Dynamic phenotype simulator
An association-conditioned membrane simulator converts gene-specific electrical fingerprints into transparent dynamic hypotheses while explicitly separating simulation from causal inference.

## Model architecture: NeuroBEAM-Fusion
Inputs:
- electrophysiology features
- transcriptomic features
- optional morphology
- cell metadata for nuisance control only

Modules:
1. Bioelectric encoder
2. Transcriptomic encoder
3. Cross-modal alignment layer
4. Explainability / sparse attribution head
5. Disease-projection head
6. Uncertainty head
7. Phenotype-conditioned dynamic simulator

### Benchmark baselines
- linear/ridge regression
- elastic net
- partial least squares
- random forest / ExtraTrees
- gradient boosting where appropriate
- PCA/factor baseline for electrical axes

### Required split strategy
Never random neuron-level train/test splitting when multiple neurons arise from one subject.
Use grouped subject/mouse splits.

## Experimental matrix
### Experiment 1 — Electrical state discovery
- robust scaling
- PCA/factor analysis
- K-means baseline
- GMM
- HDBSCAN
- consensus/stability
- bootstrap ARI/Jaccard
- label reveal only after state freezing

### Experiment 2 — Same-cell gene–electrical coupling
- Spearman discovery
- BH-FDR
- mixed/donor-aware sensitivity where possible
- within-broad-class direction consistency
- pseudobulk confirmation where replication permits

### Experiment 3 — Transcriptome → electrophysiology prediction
- GroupKFold by subject
- predict individual electrical traits and/or electrical latent axes
- R², MAE, Spearman
- calibration/uncertainty
- feature attribution stability

### Experiment 4 — Cross-region external validation
- Visual cortex discovery/training
- M1/MOp reserved external cohort
- freeze features, mappings and preprocessing before M1 evaluation
- no tuning using M1 outcomes

### Experiment 5 — Pan-cancer projection
- cBioPortal mutation-sequenced denominators
- top-500 cancer–bioelectric discovery catalog
- gene × disease × electrical-trait cube
- recurrence and prevalence metrics
- source-specific missingness retained as NA

### Experiment 6 — Dynamic simulation
- adaptive LIF + Ih-like sag
- gene-conditioned parameter shifts derived only from measured electrical association fingerprint
- baseline vs high-expression-like vs low-expression-like
- sensitivity across perturbation strength and injected current

## Ablation studies
1. remove cell-class information
2. within-class only
3. remove high-correlation electrical variables
4. remove ion-channel genes
5. remove canonical cancer-driver genes
6. cancer-only ranking vs bioelectric-only ranking vs combined ranking
7. subject-grouped vs naive random split to quantify leakage inflation
8. signed vs absolute disease-bioelectric projection
9. gene-rank normalization vs raw/normalized expression
10. dynamic model with/without sag and adaptation terms

## Negative controls
- permuted gene-expression labels within subjects
- permuted electrical traits
- random gene panels matched for expression prevalence
- shuffled cancer cohort labels
- unrelated genes with no significant electrical association

## Statistical reporting
Every principal result should report:
- neuronal n
- subject/mouse n
- disease sample denominator
- effect size
- 95% CI where estimable
- raw p
- FDR q
- validation set performance
- bootstrap stability
- missingness
- exact source/release

## Main figures
### Fig. 1 — NEURO-BEAM architecture
brain → neuron → electrophysiology → transcriptome → explainable model → disease projection → dynamic hypothesis

### Fig. 2 — Bioelectric state/axis atlas
PCA/factors, cluster stability, subtype label reveal

### Fig. 3 — Same-cell gene–electrical coupling
gene × electrical heatmap, within-class validation, key genes

### Fig. 4 — Predictive machine intelligence
grouped CV, baseline comparisons, attribution stability, calibration

### Fig. 5 — External M1 validation
frozen model transfer and performance

### Fig. 6 — Top-500 discovery landscape
cancer score vs bioelectric score, Pareto frontier, top modules

### Fig. 7 — Disease × gene × bioelectric cube
cross-cancer heatmaps and interpretable case studies

### Fig. 8 — Dynamic phenotype simulation
baseline vs gene-conditioned voltage traces, parameter shifts, sensitivity

## Manuscript results structure
1. NEURO-BEAM constructs a leakage-safe multimodal discovery framework
2. Cortical neurons exhibit reproducible bioelectric organization
3. Same-cell transcriptomes encode bioelectric phenotypes
4. Explainable models identify stable electrical gene programs
5. Frozen models generalize to an independent cortical region
6. Cross-disease genomic projection identifies recurrent bioelectric-associated programs
7. Dynamic simulation translates associations into falsifiable electrophysiological hypotheses

## Discussion boundaries
Must not claim:
- cancer mutation causes neuronal electrical change;
- mouse cortical gene–ephys correlation equals human tumour physiology;
- dynamic simulator predicts true gene perturbation response;
- cross-disease score is diagnostic/prognostic without dedicated validation.

## Positioning
The strongest journal-facing framing is machine intelligence for scientific discovery:
- multimodal representation
- leakage-safe learning
- interpretable cross-domain transfer
- falsifiable simulation
- reproducible public portal and data products

The portal is the reproducibility/interface layer; the model, validation and scientific discovery are the manuscript contribution.
