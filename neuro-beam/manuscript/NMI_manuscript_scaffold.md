# Nature Machine Intelligence — Working Manuscript Scaffold

## Working title
**NEURO-BEAM: cross-domain bioelectric evidence fusion for machine-learning-guided discovery across neuronal electrophysiology and cancer genomics**

## Alternative titles
1. **Cross-domain machine learning links neuronal bioelectric programs to recurrent cancer genomic alterations**
2. **A machine-learning discovery engine for integrating single-neuron electrophysiology with human cancer genomics**
3. **NEURO-BEAM discovers cross-domain gene signatures connecting neuronal electrical phenotypes and cancer genomic variation**

## Article type
Primary target: **Article**.
Fallback if the method remains primarily re-analysis of public data: **Analysis**.

## Central contribution
NEURO-BEAM is not presented as a portal alone. The scientific contribution is a reusable computational framework that:
1. learns gene–electrophysiology relationships from same-cell Patch-seq;
2. validates electrical-state structure independently of molecular labels;
3. integrates human cancer-genomics evidence through Cross-Domain Bioelectric Evidence Fusion (CBEF);
4. ranks genes with decomposable evidence rather than a black-box score;
5. exposes correlation-informed counterfactual neuronal simulations for hypothesis generation;
6. provides complete machine-readable provenance and reproducible workflows.

## Abstract skeleton (≤150 words)
Machine-learning methods increasingly integrate heterogeneous biomedical datasets, yet linking cellular electrophysiology to disease genomics remains difficult because the modalities are rarely measured in the same biological samples. We introduce NEURO-BEAM, a cross-domain discovery framework that learns gene–bioelectric relationships from same-cell neuronal Patch-seq and transfers those relationships into independently measured human cancer-genomics cohorts. A new Cross-Domain Bioelectric Evidence Fusion (CBEF) score combines electrical association strength, statistical evidence, cancer alteration burden and cross-cohort recurrence while retaining a complete evidence decomposition. The framework further provides correlation-informed counterfactual neuronal simulations and interactive exploration of gene-, cohort- and signal-specific hypotheses. [Insert final quantitative results after external validation and ablation.] NEURO-BEAM establishes a reproducible strategy for connecting electrophysiological phenotypes with genomic disease evidence without asserting cell-level equivalence across unmatched datasets.

## Introduction — core argument
- Multimodal biological discovery is limited by non-overlapping cohorts and modalities.
- Patch-seq gives rare same-cell electrophysiology + transcriptomics.
- Large cancer resources give independent disease-genomic context.
- Naive concatenation across unmatched cohorts is invalid.
- Need a principled cross-domain evidence-fusion method that preserves modality provenance.
- NEURO-BEAM addresses this gap with same-cell learning + independent disease evidence + transparent fusion + external validation.

## Results
### 1. A matched-cell bioelectric–transcriptomic atlas
- n matched neurons
- n genes
- n electrical traits
- strongest associations
- within-class sensitivity analysis
- donor-aware analysis

### 2. Unsupervised electrical-state structure is reproducible but not reducible to cell type
- PCA / latent electrical axes
- consensus clustering
- bootstrap stability
- transcriptomic label reveal
- external motor-cortex validation

### 3. CBEF integrates independent disease-genomic evidence without cross-cohort pseudo-matching
- ortholog mapping
- cancer cohort mutation denominators
- score definition
- top-500 catalog
- score decomposition

### 4. CBEF improves discovery stability relative to single-view rankings
Required benchmarks:
- bioelectric-only ranking
- cancer-only ranking
- simple rank sum
- Fisher/Stouffer evidence combination
- CCA / PLS baseline
- random-weight fusion
- CBEF
Evaluate:
- bootstrap top-k overlap
- perturbation stability
- external M1 replication enrichment
- pathway coherence

### 5. Top-ranked genes define interpretable electrical programs
- channel genes
- calcium signaling
- mitochondrial regulation
- activity-dependent programs
- DNA repair/chromatin
Avoid overinterpreting cancer causality.

### 6. Correlation-informed counterfactual simulations support mechanistic hypothesis generation
- baseline vs selected-gene simulation
- phenotype-constrained mode
- conductance-aware mode for curated ion-channel genes
- sensitivity to perturbation strength
- no claim of causal biophysical parameter estimation

### 7. NEURO-BEAM provides a reusable discovery platform
- full CSV/JSON
- GitHub Actions reproducibility
- live web explorer
- code/data provenance
- testable external hypotheses

## Discussion
- Main methodological advance
- Why unmatched datasets require evidence fusion rather than concatenation
- Interpretability and hypothesis generation
- Limitations:
  - mouse neuronal physiology vs human tumors
  - cancer mutation prevalence is not neuronal mutation biology
  - correlations are not perturbational effects
  - simulator is normalized counterfactual
  - current external validation is cortical, not disease-specific
- Future experimental validation

## Methods
### Data sources
### Same-cell alignment
### Electrophysiology QC
### Bioelectric association testing
### Ortholog mapping
### Cancer mutation retrieval
### CBEF
### Ranking stability
### External validation
### Counterfactual simulation
### Software and reproducibility
### Statistical analysis

## Data availability
Public source datasets remain at their authoritative repositories. NEURO-BEAM releases processed association tables, rankings, analysis-ready matrices and provenance manifests.

## Code availability
GitHub repository and live portal URLs to be inserted in final version.

## AI-use disclosure
Any use of generative AI for language assistance, code drafting or organization must be transparently disclosed and independently verified by the authors, in line with current Nature Portfolio policy. Scientific judgement, analyses, conclusions and accountability remain with the authors.
