# NEURO-BEAM Current Results Snapshot — 2026-09-21

## Discovery cohort
- 3,654 matched visual-cortex Patch-seq neurons
- 1,302 genes in the filtered expression matrix
- 18 measured electrical traits used in the gene–bioelectric association layer

## Subject-grouped predictive benchmark
5-fold GroupKFold using subject IDs parsed from electrophysiology identifiers.

Best current baseline: **Extra Trees, 400 high-variance genes**
- mean trait R² = **0.341**
- median trait R² = **0.269**
- mean held-out Spearman = **0.612**

Selected traits:
- AP upstroke/downstroke ratio: R² **0.750**, Spearman **0.906**
- membrane time constant: R² **0.605**, Spearman **0.865**
- long-square threshold current: R² **0.679**, Spearman **0.802**
- input resistance: R² **0.558**, Spearman **0.795**
- ramp threshold current: R² **0.559**, Spearman **0.753**
- F-I slope: R² **0.552**, Spearman **0.649**

These results support a predictive relationship between transcriptomic state and several electrical phenotypes, while some traits remain weakly predicted.

## CBEF Top-ranked genes
Current leading genes include:
1. SLIT2
2. FAM135B
3. DSCAM
4. CACNA2D3
5. EGFR
6. NRXN1
7. KCNT2
8. GRIN3A
9. CNTNAP4
10. CSMD3

Additional high-ranked excitability genes include SCN1A, HCN1, CACNA1A, KCNH7, ITPR1 and CACNA1E.

## Independent motor-cortex transfer
External dataset: 1,328 M1 Patch-seq neurons.

CBEF Top-500 Ridge:
- mean external Spearman across 8 matched traits = **0.244**
- median external Spearman = **0.318**
- mean external standardized R² = **-0.065**

Strongest transferred traits:
- AP upstroke/downstroke ratio: Spearman **0.615**, R² **0.200**
- membrane time constant: Spearman **0.432**, R² **0.195**
- input resistance: Spearman **0.368**, R² **0.078**
- rheobase: Spearman **0.365**
- sag ratio: Spearman **0.272**, R² **0.074**

Adaptation does not transfer well and shows a negative rank association in the current cross-region mapping.

## Interpretation
The current evidence supports:
- strong within-discovery predictive structure;
- a reproducible cross-domain gene ranking;
- selective external generalization for several electrophysiological traits.

The current evidence does **not** support:
- universal cross-region prediction;
- causal effects of cancer mutations on neuronal physiology;
- direct physical interpretation of counterfactual simulator parameter shifts.

## Required next analyses before Nature Machine Intelligence submission
- full CBEF weight sensitivity and cohort bootstrap
- negative-control fusion permutations
- repeat predictive benchmark after Top-500 rerun
- alternative fusion baselines
- confidence intervals for external transfer
- pathway enrichment / biological coherence
- software tests and release tagging
