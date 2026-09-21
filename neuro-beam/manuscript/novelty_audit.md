# NEURO-BEAM Novelty Audit and Defensible Claim Set

## Why a narrow novelty claim is necessary
Several existing methods already demonstrate that transcriptomic data can predict or relate to neuronal electrophysiology.

### Relevant precedent
1. **UnitedNet** (Nature Communications, 2023) performs explainable multi-task learning on multimodal biological data and applies cross-modal prediction to Patch-seq electrophysiology, transcriptomics and morphology.
   - https://www.nature.com/articles/s41467-023-37477-x

2. **PERSIST** (Nature Communications, 2023) includes a Patch-seq demonstration selecting genes predictive of electrophysiological properties.
   - https://www.nature.com/articles/s41467-023-37392-1

3. **NEUROeSTIMator** (Nature Communications, 2024) uses deep learning on transcriptomics to quantify neuronal activation and demonstrates association with Patch-seq electrophysiological features across biological contexts.
   - https://www.nature.com/articles/s41467-023-44503-5

4. **COSIME** (Nature Machine Intelligence, 2025) introduces cooperative multi-view integration with learnable optimal transport, deep networks and interpretable cross-view interactions.
   - https://www.nature.com/articles/s42256-025-01111-w

5. **COMET** (Nature Machine Intelligence, 2025) uses transfer learning to leverage large observational clinical data to improve smaller omics analyses.
   - https://www.nature.com/articles/s42256-024-00974-9

6. **Deep latent variable path modelling** (Nature Machine Intelligence, 2025) integrates multimodal cancer data through a learned latent/path framework.
   - https://www.nature.com/articles/s42256-025-01052-4

## Claims NEURO-BEAM should NOT make
- first method to predict electrophysiology from transcriptomics;
- first multimodal Patch-seq integration method;
- first machine-learning method for cancer multi-omics;
- causal inference of cancer mutations on neuronal electrical physiology;
- direct cell-level integration between cancer samples and Patch-seq neurons.

## Defensible methodological novelty
NEURO-BEAM is positioned around the following combined contribution:

### 1. Provenance-preserving cross-domain evidence fusion
The framework integrates evidence from modalities that are **not observed in the same biological samples** without pretending that they are matched. Same-cell Patch-seq provides the neuronal gene–electrical relationship; independent human cancer cohorts provide disease-genomic evidence.

### 2. CBEF — decomposable cross-domain ranking
Cross-Domain Bioelectric Evidence Fusion ranks orthologous genes using separately measurable:
- neuronal bioelectric evidence;
- cancer genomic recurrence/burden;
- a cross-domain synergy term.

The evidence decomposition remains inspectable for every gene.

### 3. Cross-domain prior-guided electrophysiology learning
CBEF-derived priors are tested as feature priors in a shared latent multi-task electrophysiology predictor and compared against:
- unweighted latent learning;
- bioelectric-only priors;
- cancer-only priors;
- generic predictive baselines.

The scientific question is whether disease-genomic evidence can improve selection/representation of genes carrying electrophysiological information.

### 4. Stability-aware discovery rather than one-shot ranking
Ranking claims require:
- fusion-weight sensitivity;
- cancer-cohort bootstrap;
- negative-control permutations;
- top-k selection frequencies;
- external cross-region electrophysiology validation.

### 5. Counterfactual hypothesis-generation interface
Selected genes drive normalized electrophysiology counterfactuals using only observed neuronal gene–electrical associations. Cancer mutation frequency is deliberately excluded from voltage generation.

## Strongest possible manuscript claim if validation succeeds
> A provenance-preserving cross-domain evidence-fusion framework can prioritize genes that jointly carry reproducible neuronal electrophysiological information and recurrent human disease-genomic evidence, while retaining interpretable evidence decomposition and selective cross-region predictive transfer.

This remains an association/discovery claim, not a causal mechanism claim.

## Nature Machine Intelligence fit
The manuscript should emphasize:
- the machine-learning/evidence-fusion problem;
- quantitative comparison with strong integration and prediction baselines;
- generalization/stability;
- broad utility of the methodological principle for unmatched biomedical modalities;
- reproducible software and inspectable evidence.

The web portal is a deployment and interpretability layer, not the central scientific novelty.
