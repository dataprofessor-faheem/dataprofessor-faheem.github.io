# CBEF v1.0 — Cross-Domain Bioelectric Evidence Fusion

## Purpose
CBEF ranks genes for cross-domain discovery by combining independent evidence from same-cell neuronal electrophysiology/transcriptomics and human cancer somatic-genomics cohorts.

## Evidence views
**Bioelectric view**
- strongest absolute Spearman association across measured electrophysiology traits
- number of BH-FDR significant electrical traits
- statistical evidence strength (-log10 minimum BH-FDR q)

**Cancer view**
- mean mutation prevalence across selected mutation-sequenced cohorts
- maximum cohort mutation prevalence
- recurrence breadth across cohorts

All component variables are converted to percentile ranks before fusion, preventing variables with larger numerical scales from dominating the score.

## Scores
Bioelectric evidence:
B = mean(percentile(max |rho|), percentile(significant trait count), percentile(-log10 min q))

Cancer evidence:
C = mean(percentile(mean mutation %), percentile(max mutation %), percentile(cohort breadth))

Cross-domain synergy:
S = sqrt(B*C)

CBEF discovery score:
D = 0.45 B + 0.35 C + 0.20 S

The current weights are pre-specified engineering weights and must be subjected to sensitivity analysis and ablation before manuscript claims are finalized.

## Counterfactual simulator
The dynamic neuron simulator is parameterized ONLY from the electrophysiology-association view. Cancer mutation prevalence never changes membrane voltage directly.

For a selected gene, the portal maps correlation coefficients to normalized perturbation controls for:
- resting potential
- input resistance
- membrane time constant
- F-I gain
- adaptation
- latency
- sag
- threshold current/voltage
- spike kinetics

These mappings are explanatory normalized counterfactuals, not causal estimates in physical units.

## Required manuscript validation
- weight sensitivity / ranking stability
- alternative fusion baselines
- donor-aware predictive validation
- external M1 replication
- cross-species symbol mapping audit
- negative-control genes
- bootstrap confidence intervals
- ablation of each evidence view
