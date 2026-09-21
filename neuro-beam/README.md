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
