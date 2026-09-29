# Chlamydia AI MathFusion

Live research prototype for AI-assisted Chlamydia inclusion-body analysis in Giemsa and DFA/fluorescence microscopy.

## Live site
Published as a subdirectory of the GDR Network GitHub Pages site:
`/chlamydia-ai/`

## Scientific status
The front end is live. Chlamydia-specific inference remains intentionally disabled until a Chlamydia-labelled model has been trained and independently validated. Generic pretrained cell models must not be represented as a validated pathogen diagnostic.

## Architecture
Teacher stack:
- CellSAM
- Cellpose-SAM / CPDINO
- micro-SAM
- StarDist

Deployable student:
- YOLO26-seg after Chlamydia-specific fine-tuning/distillation

Mathematical layer:
- simplex-constrained calibrated teacher weighting
- Focal-Tversky + Dice loss
- boundary and signed-distance geometry
- knowledge distillation
- Giemsa/DFA Jensen-Shannon consistency
- optional entropy-regularized optimal transport for paired embeddings
- Brier calibration and uncertainty-based manual review

## Leakage rule
Split by experiment / plate / well / biological replicate. Never split random crops from the same microscopy field across train and test sets.
