# Pre-specified Phase-1 Analysis Protocol

## Primary hypothesis
Distinct cortical neurons occupy reproducible electrophysiological states/axes that are associated with transcriptional programs beyond broad cell-type identity and generalize to an independent cortical region.

## Primary outcome
A frozen Bioelectric Gene Signature (BGS) derived from same-neuron electrophysiology + transcriptomics and externally validated.

## Discovery separation
Bioelectric state discovery is performed using electrophysiology only. Transcriptomic labels and known cell labels are revealed only after electrical states/axes are frozen.

## Bioelectric-state discovery
- robust feature scaling
- Spearman correlation architecture
- PCA plus parallel/scree/stability assessment
- candidate clustering: GMM, hierarchical, HDBSCAN, k-means baseline
- cluster choice using silhouette, Calinski-Harabasz, Davies-Bouldin and resampling stability
- if data are continuous, report continuous axes instead of forcing clusters

## Donor-aware inference
Use mixed-effects models with donor/animal random intercepts when repeated neurons arise from the same animal. Transcriptomic confirmation should include pseudobulk aggregation when biological replication supports it.

## Transcriptomic coupling
For gene g: expression ~ electrical_state/axis + cell_subclass + layer + batch + (1|donor).
Report effect size, 95% CI, raw P and BH-FDR.

## Signature criteria
A final BGS gene should preferably satisfy: significant donor-aware association, meaningful effect size, bootstrap stability, within-subtype persistence, cross-region direction concordance, and out-of-sample predictive value.

## ML validation
Split by donor/animal, not neuron. All scaling, imputation, feature selection and tuning occur inside the training folds. External DANDI 000008 data remain untouched until final validation.