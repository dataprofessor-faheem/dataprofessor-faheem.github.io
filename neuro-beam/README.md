# NEURO-BEAM
## Neuronal BioElectricity–Activity–Molecular Atlas

**NEURO-BEAM** is a scientific Bio-IT research platform developed for integrated exploration of neuronal bioelectric phenotypes, molecular signatures and comparative disease genomics.

**Developed by:**  
**Dr. Mohd Faheem Khan** and **Dr. Khurshid Ahmad**  
Founders & Lead Scientists, **GDRN Network**

### Scientific purpose
NEURO-BEAM provides researchers with an interactive environment for bioelectric-signal exploration, gene-level molecular interrogation, cross-cohort cancer-genomics comparison and analysis-ready numerical exports. The platform is intended for hypothesis generation, comparative computational research and downstream statistical investigation.

### Research capabilities
- Neuronal bioelectric phenotype exploration
- Same-cell gene–electrophysiology association analysis
- Cancer cohort × gene × electrical-signal signature exploration
- Exact mutation prevalence, Spearman rho, BH-FDR and matched-neuron sample size
- Cross-cohort comparative visualization
- Analysis-ready CSV exports for independent research

### Citation
Khan MF, Ahmad K. *NEURO-BEAM: Neuronal BioElectricity–Activity–Molecular Atlas*. GDRN Network. Available at: https://www.gdrnetwork.org/neuro-beam/

### Research interpretation
Cross-domain molecular and bioelectric associations are provided for scientific exploration and hypothesis generation. They should not be interpreted as causal or clinical effects without appropriate experimental or clinical validation.

**Platform:** https://www.gdrnetwork.org/neuro-beam/


## NEURO-BEAM Discovery Studio Release

Current validated release components:

- 3,654 matched visual-cortex Patch-seq neurons
- 936 reconstructed subjects used for leakage-safe grouped validation
- 1,302 Patch-seq genes tested against 18 electrical traits
- 1,268 genes mapped into the human pan-cancer projection
- Top-500 cancer–bioelectric discovery catalog
- 5,000 Top-500 gene × cancer cohort rows
- 9,000 Top-500 gene × electrical-trait rows
- 500 gene-conditioned dynamic membrane models
- 1,304-cell independent M1 external validation cohort
- 15/15 publication-engineering integrity checks passed

### Machine-learning evidence
Subject-grouped ExtraTrees performance is strongest for:
- AP upstroke/downstroke ratio: mean Spearman ≈ 0.909
- membrane time constant: ≈ 0.874
- threshold current: ≈ 0.808
- input resistance: ≈ 0.799

Frozen cross-region M1 rank transfer is strongest for:
- AP upstroke/downstroke ratio: Spearman ≈ 0.627
- threshold-current/rheobase comparison: ≈ 0.612
- input resistance: ≈ 0.556
- membrane time constant: ≈ 0.500

### Primary research downloads
- data/top500_cancer_bioelectric_genes.csv
- data/top500_cancer_matrix.csv
- data/top500_bioelectric_matrix.csv
- data/top500_dynamic_model_parameters.csv
- data/cancer_gene_bioelectric_signature_cube.csv
- data/ml_grouped_cv_summary.csv
- data/m1_external_validation_metrics.csv
- data/release_status.json

### Manuscript package
- manuscript/NMI_manuscript_v1.md
- manuscript/NMI_cover_letter_draft.md
- docs/nmi_manuscript_blueprint.md
- docs/scientific_release_gates.md

The release audit indicates artifact completeness and internal reproducibility readiness only; it does not predict editorial acceptance.
