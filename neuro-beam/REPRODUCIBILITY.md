# NEURO-BEAM Reproducibility Guide

## Design principle
Every manuscript-level result must be traceable through:

**authoritative source data → deterministic processing script → versioned result file → portal visualization / manuscript figure**

The public portal is a presentation layer; CSV/JSON outputs are the scientific record used by downstream figures.

## Clean-checkout reproduction order

1. Visual-cortex discovery
   `python code/05_visual_cortex_discovery.py`

2. State stability validation
   `python code/06_state_stability_validation.py`

3. cBioPortal study catalog
   `python code/07_build_cbioportal_catalog.py`

4. Disease mutation bridge
   `python code/08_disease_bioelectric_bridge.py`

5. Same-cell bioelectric–transcriptomic coupling
   `python code/10_bioelectric_disease_coupling.py`

6. Cancer × gene × signal cube
   `python code/12_build_signature_cube.py`

7. CBEF Top-500 discovery
   `python code/13_top500_discovery_engine.py`

8. Dynamic counterfactual model parameters
   `python code/14_build_dynamic_models.py`

9. Leakage-safe predictive benchmark
   `python code/15_predictive_benchmark.py`

GitHub Actions workflows implement the same sequence online.

## Determinism
- fixed random seeds are used for stochastic baseline analyses;
- train/test separation is subject-grouped;
- API retrieval failure is encoded as unavailable, never converted to a biological zero;
- raw public-source data are not silently modified;
- cross-species mappings and denominators are exported with outputs.

## Scientific firewalls
- cancer evidence does not directly alter membrane voltage in the simulator;
- transcriptomic labels are not used to create initial electrical states;
- external validation data are kept outside discovery fitting;
- counterfactual model controls are correlation-informed normalized parameters, not causal physical estimates.

## Main evidence files
- `data/visual_cortex_discovery.json`
- `data/visual_cortex_stability_validation.json`
- `data/bioelectric_gene_associations.csv`
- `data/disease_bioelectric_bridge.json`
- `data/cancer_gene_bioelectric_signature_cube.csv`
- `data/top500_gene_catalog.csv`
- `data/top500_cancer_matrix.csv`
- `data/top500_bioelectric_matrix.csv`
- `data/top500_dynamic_model_parameters.csv`
- `data/predictive_benchmark_summary.csv`

## Before manuscript submission
- freeze a tagged release;
- archive the release and source-data tables with a DOI;
- add exact package versions;
- add automated tests;
- verify every manuscript number against a source-data table;
- provide an executable compute capsule or container for reviewers.
