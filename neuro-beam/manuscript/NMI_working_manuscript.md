# NEURO-BEAM Manuscript Working Draft

## Title
NEURO-BEAM: Explainable Machine Intelligence Links Neuronal Bioelectric Phenotypes to Cross-Disease Genomic Programs

## Abstract — working version
Neuronal identity is encoded jointly by molecular state and electrophysiological behaviour, yet scalable frameworks that connect these domains to disease-associated genomic variation remain limited. We developed NEURO-BEAM, an explainable multimodal machine-intelligence framework that integrates same-cell Patch-seq electrophysiology and transcriptomics with independent disease-genomics cohorts while explicitly preserving source separation. In mouse visual-cortex Patch-seq neurons, the framework constructs reproducible bioelectric representations, quantifies gene–electrical associations across measured membrane and firing traits, and tests whether transcriptomic information predicts electrical phenotypes under subject-grouped validation. Molecular programs are subsequently projected into independent cancer-genomics cohorts using mutation-sequenced denominators and auditable mouse-to-human gene mapping, yielding a cancer × gene × bioelectric-trait discovery space rather than a causal disease model. A phenotype-constrained dynamic simulator translates observed electrical association fingerprints into falsifiable membrane-dynamics hypotheses. NEURO-BEAM is released with machine-readable matrices, provenance, uncertainty and an interactive research portal. The framework provides a general strategy for using interpretable machine intelligence to connect cellular physiology with molecular and disease-level genomic organization while avoiding naive concatenation of unmatched biological datasets.

## Introduction — argument skeleton
### Paragraph 1
Electrical phenotype is a core dimension of neuronal identity, but genomic and transcriptomic atlases often emphasize molecular taxonomies without directly modelling how those molecular states relate to membrane physiology.

### Paragraph 2
Patch-seq provides a same-cell bridge between electrophysiology and transcriptomics, creating an opportunity for multimodal learning in which the biological correspondence is experimentally matched rather than computationally assumed.

### Paragraph 3
Disease-genomics resources provide a separate opportunity: once molecular programs associated with electrical phenotypes are identified, their alteration across disease cohorts can be examined as an independent-source projection. This projection must not be interpreted as same-cell evidence or causality.

### Paragraph 4
Existing analysis approaches often stop at pairwise correlations, cell-type classification or disease-specific genomic visualization. A framework is needed that combines leakage-safe representation learning, interpretable multimodal prediction, external validation, cross-domain projection and falsifiable dynamic hypothesis generation.

### Paragraph 5
Here we introduce NEURO-BEAM and test whether neuronal bioelectric organization can be learned reproducibly, predicted from transcriptomic state, generalized across cortical regions and connected to independent disease-genomic programs through explainable computational transfer.

## Results
### 1. A reproducible architecture separates matched multimodal learning from cross-domain transfer
[TABLE/FIGURE placeholders populated automatically from release outputs.]

### 2. Electrophysiological features define stable bioelectric organization
[Insert final consensus/stability results.]

### 3. Same-cell transcriptomes encode electrical phenotype
[Insert grouped-CV predictive results and gene association results.]

### 4. Interpretable molecular features support electrical prediction
[Insert top feature stability, pathways, ablation.]

### 5. Frozen models generalize to M1
[Insert external validation.]

### 6. Top-500 cancer–bioelectric projection identifies recurrent cross-domain programs
[Insert final top-500 discovery results after release gates.]

### 7. Gene-conditioned dynamic simulation generates falsifiable electrophysiological hypotheses
[Insert simulator cases and sensitivity.]

## Methods
- datasets and releases
- preprocessing/QC
- ID alignment
- electrical feature filtering
- clustering/stability
- association/FDR
- grouped ML
- external validation
- cBioPortal retrieval
- human ortholog mapping
- discovery ranking
- dynamic model equations
- software/reproducibility

## Limitations
- primary same-cell evidence is mouse cortical Patch-seq
- cross-cancer projection uses independent human tumour cohorts
- mutation prevalence is not neuronal tissue physiology
- dynamic simulation is association-conditioned, not gene-perturbation causal modelling
- external validation and perturbational follow-up determine generalizability
