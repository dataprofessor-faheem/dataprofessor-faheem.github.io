# NEURO-BEAM End-to-End Release Report

## Workflow

Brain region → Neuron identity → Bioelectric state → Gene regulation → Regulatory context → Prediction

### 1. Brain region
- Status: **integrated reference + external validation**
- Evidence: VIS discovery; M1 external validation; ABC Atlas/MERFISH reserved for spatial projection
- Key result: Visual cortex is the discovery region; primary motor cortex is held out for external generalization.
- Guardrail: ABC Atlas/MERFISH is a spatial reference layer, not same-cell Patch-seq evidence in the current release.

### 2. Neuron identity
- Status: **same-cell measured**
- Evidence: Patch-seq transcriptomics + electrophysiology; broad neuronal class metadata
- Key result: 3654 matched neurons from 936 subjects support subject-grouped inference.
- Guardrail: Identity labels are used for stratification/robustness checks, not to define molecular-electrical causality.

### 3. Bioelectric state
- Status: **measured + unsupervised**
- Evidence: Electrophysiology; PCA; K-means/GMM/HDBSCAN; bootstrap stability
- Key result: Physiology-only discovery retained 27 features; bootstrap ARI=0.850.
- Guardrail: Candidate electrical states remain descriptive; unstable/rare states are not assigned biological names.

### 4. Gene regulation
- Status: **same-cell association + evidence tiers**
- Evidence: 1,302-gene Patch-seq matrix; BH-FDR gene–ephys coupling; Top-500/Pareto evidence
- Key result: 1302 genes were tested against measured electrical traits; Top-500 evidence catalog and tiering are available.
- Guardrail: Associations are transcriptomic correlates of electrical phenotypes; TF/pathway interpretation is secondary unless directly tested.

### 5. Regulatory context
- Status: **proxy + external context**
- Evidence: DNA-repair/chromatin gene modules; neurological-disease evidence; 4DN/SMaHT contextual resources
- Key result: 199 Top-500 genes have neurological-disease evidence; regulatory/chromatin interpretation is carried as contextual evidence.
- Guardrail: No same-cell chromatin assay is present in the core Patch-seq cohort; chromatin/DNA-repair claims are proxy/contextual, not directly measured.

### 6. Prediction
- Status: **validated baseline**
- Evidence: 5-fold GroupKFold by subject; ExtraTrees/Ridge; permutation controls; conformal coverage; untouched M1 evaluation
- Key result: ExtraTrees is the current validated production baseline; NeuroBEAM-Net denotes the framework, not an unvalidated deep model.
- Guardrail: External M1 rank generalization is trait-dependent and calibration/domain shift can be substantial; do not convert predictions into clinical or causal claims.

## Prediction release

- Validated production baseline: ExtraTrees regression with fold-local top-300 variance genes
- Validation: 5-fold GroupKFold by subject ID
- Cells / subjects / genes: 3654 / 936 / 1302
- Compatible external M1 traits: 9
- Mean external M1 Spearman across compatible traits: 0.315

## Interpretation boundary

This end-to-end release integrates measured, external, proxy and predicted evidence. These evidence classes must not be collapsed into a single causal chain.