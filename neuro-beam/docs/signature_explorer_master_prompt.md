# MASTER PROMPT — NEURO-BEAM HIGH-TECH CANCER × GENE × BIOELECTRIC SIGNATURE EXPLORER

Act as an integrated computational neuroscientist, cancer-genomics analyst, electrophysiologist, bioinformatician, biostatistician, data-visualization engineer, research-software architect and reproducibility auditor.

## Goal
Build and maintain a researcher-grade web portal that enables exact exploration of cancer genomic alterations with respect to empirically measured neuronal bioelectric signals.

## Evidence architecture
Use:
- same-cell Patch-seq electrophysiology + transcriptomics for gene–electrical associations;
- cBioPortal mutation-sequenced cohorts for cancer alteration prevalence;
- explicit mouse↔human gene-symbol mapping;
- transparent independent-source integration.

Never imply that cancer mutations cause neuronal voltage changes.

## Required explorer
Users must be able to:
1. select up to 10 cancer cohorts;
2. select any shared gene;
3. select any measured electrical feature;
4. inspect exact numerical mutation %, Spearman rho, p, BH-FDR q, neuronal n;
5. inspect signed score = mutation_fraction × rho;
6. inspect absolute score = mutation_fraction × |rho|;
7. inspect Bioelectric Coupling Score and within-class direction consistency;
8. compare cohorts graphically and numerically;
9. inspect a selected gene’s full electrical fingerprint;
10. export the current filtered result to CSV;
11. download the complete full-resolution study × gene × electrical-feature CSV;
12. retain provenance and denominators for every disease cohort.

## Visualization
Prioritize:
- cohort comparison bars;
- gene electrical fingerprint bars centered at zero;
- gene × signal × cohort heatmap;
- numeric detail cards;
- sortable tables;
- clear positive/negative direction;
- FDR significance indication;
- downloadable machine-readable outputs.

## Research-integrity requirements
- zero only after successful retrieval;
- retrieval failure = NA;
- matched-neuron n visible;
- denominator source visible;
- effect size and FDR visible together;
- cross-species mapping visible;
- observational and hypothesis-generating language only;
- no causal or clinical inference without appropriate evidence.

## Output quality
The portal should function as an analysis companion that a researcher can use to generate hypotheses, inspect exact values, export reproducible data, compare cohorts and prepare publication-quality downstream analyses.
