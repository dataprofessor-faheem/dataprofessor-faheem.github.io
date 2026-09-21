# NEURO-BEAM Scientific Release Gates

A result may be labelled **validated** only if its applicable gates pass.

## Gate A — Data integrity
- exact source accession recorded
- cell/study identifiers traceable
- failed retrieval = NA, never zero
- denominator documented
- cross-species mapping retained
- no silent duplicate IDs

## Gate B — Bioelectric discovery
- protocol/timing artifacts excluded
- cluster/axis result stable under resampling
- rare clusters flagged
- UMAP never used as cluster evidence
- biological labels not used to construct electrical states

## Gate C — Association
- effect size reported
- FDR q reported
- n reported
- within-class sensitivity completed for headline genes
- direction consistency reported

## Gate D — Machine learning
- subject-grouped split
- preprocessing inside folds
- no external-validation tuning
- at least two simple baselines
- ablation and permutation control
- confidence interval on performance

## Gate E — Disease projection
- mutation-sequenced denominator
- non-zero only after successful retrieval
- missing queries represented NA
- mouse/human mapping auditable
- projection described as independent-source integration

## Gate F — Dynamic simulation
- model equations published
- mapping from measured trait correlation to parameter shift published
- simulation labelled phenotype-constrained/non-causal
- sensitivity to strength/current reported
- raw simulation parameters downloadable

## Gate G — Manuscript readiness
- all headline figures reproducible from repository
- figure source tables exported
- exact software versions recorded
- README execution path works in clean environment
- limitations explicitly match analysis architecture
