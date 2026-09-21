# NEURO-BEAM Cancer–Gene–Bioelectric Signature Explorer

## Research objective
Create a reproducible three-dimensional exploration environment linking:
1. cancer cohort-specific somatic mutation prevalence;
2. user-selected genes;
3. measured neuronal bioelectric traits from same-cell Patch-seq.

The portal must allow exact numerical inspection, cross-cohort comparison, signed/absolute signal weighting, and CSV export suitable for downstream statistical analysis.

## Core data cube
Each record represents:

Study × Gene × Electrical feature

Required fields:
- study_id
- study_name
- cancer_type
- mutation_sequenced_n
- gene
- mouse_gene
- electrical_feature
- spearman_rho
- p_value
- bh_fdr_q
- matched_neuron_n
- mutation_percent
- signed_mutation_bioelectric_score = mutation_fraction × rho
- absolute_mutation_bioelectric_score = mutation_fraction × |rho|
- bioelectric_coupling_score
- same_direction_fraction_across_classes
- classes_tested
- source / provenance fields

## Interactive research functions
- Select one or multiple cancer cohorts (up to 10)
- Select a specific gene
- Select a specific electrical signal
- Display exact numerical values without rounding loss in downloadable data
- Compare mutation prevalence across cohorts
- Compare signed bioelectric effect across cohorts
- Compare absolute bioelectric-weighted burden across cohorts
- Show gene-specific electrical fingerprint across all 18 traits
- Show cohort-specific gene × electrical-signal matrix
- Show direction (positive/negative neuronal correlation)
- Display BH-FDR and matched-neuron sample size
- Export current filtered selection as CSV
- Download complete full-resolution cube CSV
- Download gene-level and disease-level summary files

## Integrity rules
- A zero mutation frequency is shown only after successful molecular retrieval.
- API retrieval failure is NA, never zero.
- Bioelectric correlations are computed only on explicitly matched Patch-seq neurons.
- Cancer mutation data and neuronal electrophysiology are independent observational sources.
- Cross-domain scores are hypothesis-generation metrics and are not causal effect estimates.
- Mouse/human symbols are mapped transparently and preserved in output.
- No clinical recommendation is inferred from these scores.

## Research significance
This design enables researchers to move from broad pathway-level exploration to a precise question such as:

> In glioblastoma, what is the mutation prevalence of EGFR, what numerical association does neuronal EGFR expression have with threshold current or AP upstroke/downstroke ratio, what is its FDR, and how does the signed coupling compare with lung, breast, melanoma, or colorectal cohorts?

That exact query can be inspected interactively and exported as a reproducible row set for independent downstream analysis.
