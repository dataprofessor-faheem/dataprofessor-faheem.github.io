# NEURO-BEAM
## Neuronal BioElectricity–Activity–Molecular Atlas

Live project: https://www.gdrnetwork.org/neuro-beam/

NEURO-BEAM is a reproducible public-data research framework designed to discover neuronal bioelectric states, link them to transcriptional regulation, validate them across cortical regions, and later integrate spatial brain mapping, morphology/connectomics, chromatin context and somatic-mosaicism evidence.

### Phase 1 locked datasets
- DANDI 000020 — discovery
- DANDI 001455 — excitatory discovery extension
- DANDI 000008 — untouched external validation
- Allen ABC Atlas — spatial extension
- MICrONS — structural/connectomic extension
- 4D Nucleome — regulatory context
- NIH SMaHT — somatic-mosaicism context

### Reproducibility rules
- Donor/animal-level splitting; never neuron-level leakage across train/test.
- Raw counts and raw waveforms are never overwritten.
- Preprocessing, imputation and feature selection happen inside training folds.
- UMAP is visualization, not evidence of cluster existence.
- Inference reports effect size, 95% CI, FDR, neuron count and donor count.
- Association is not described as causal without perturbational evidence.

Large raw neuroscience data are not committed to this repository. They remain at their authoritative public archives and are accessed programmatically or selectively streamed.


### First verified data ingestion
The external-validation M1 Patch-seq processed release is now ingested at metadata/feature level:
- 1,329 metadata neurons
- 1,328 matched electrophysiology neurons
- 266 unique mice
- 29 electrophysiological features
- sex: 645 male, 684 female
- major RNA families: Pvalb 289, Sst 272, IT 254, Vip 153, CT 106, Lamp5 91

This cohort remains excluded from discovery tuning and is reserved for frozen-signature validation.


## Cancer × Gene × Bioelectric Signature Explorer

The live portal now includes a research-grade 3D signature cube:

- 10 cancer cohorts
- 15 shared genes
- 18 measured neuronal electrical traits
- 2,700 study × gene × signal records

Each record contains mutation-sequenced cohort size, mutation prevalence, Spearman rho, p-value, BH-FDR q, matched-neuron n, signed mutation × bioelectric score, absolute score, Bioelectric Coupling Score, direction-consistency metrics and provenance.

Downloads:
- data/cancer_gene_bioelectric_signature_cube.csv
- data/bioelectric_gene_associations.csv
- data/bioelectric_gene_scores.csv
- data/disease_bioelectric_scores.csv

Documentation:
- docs/signature_explorer_plan.md
- docs/signature_explorer_master_prompt.md

The explorer supports user-selected cohorts, gene and electrical signal, exact numerical comparison and filtered CSV export. Cross-domain results are exploratory and association-based; they are not causal or clinical effect estimates.
