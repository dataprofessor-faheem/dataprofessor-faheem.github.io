# BEAM-Factor

BEAM-Factor learns a shared latent representation of genes from two independent evidence views:

- signed gene × neuronal electrical-trait associations;
- gene × cancer-cohort somatic-mutation prevalence.

For standardized matrices E and C, it minimizes:

L = ||W_E ⊙ (E - U V_E^T)||²_F
  + α ||W_C ⊙ (C - U V_C^T)||²_F
  + λ (||U||²_F + ||V_E||²_F + ||V_C||²_F)

where U is the shared gene embedding, V_E and V_C are view-specific loadings and α controls cancer-view weight.

## Evaluation
1. 10% masked-entry reconstruction in every electrical trait and every cancer cohort.
2. Rank/weight grid comparison.
3. External M1 validation: compare gene-level electrical-association patterns in motor cortex with:
   - raw V1 associations;
   - electrophysiology-only factor reconstruction;
   - joint BEAM-Factor reconstruction.

## Interpretation
A gain from the joint model indicates statistically useful shared structure between the independent evidence views. It does not imply that cancer mutations cause neuronal electrophysiological changes.
