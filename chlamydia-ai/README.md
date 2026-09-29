# Chlamydia AI MathFusion

Research prototype for AI-assisted Chlamydia inclusion-body analysis in Giemsa and DFA/fluorescence microscopy.

## Hosting status

The source is committed and deployment-ready. GitHub Pages is currently unavailable because the repository-level Pages service is not enabled for the connected integration. A Render Blueprint is now present at the repository root (`/render.yaml`) and targets this directory as a static site.

### Deploy on Render

Use Render with this repository and the root-level `render.yaml` Blueprint.

Repository:
`https://github.com/dataprofessor-faheem/dataprofessor-faheem.github.io`

Expected Render service name:
`chlamydia-ai-mathfusion`

Because the repository is private, Render must be granted GitHub access to this repository before the Blueprint can clone and deploy it.

## Scientific status

The web interface is a research/demo interface. Chlamydia-specific inference remains intentionally disabled until a Chlamydia-labelled model has been trained and independently validated. Generic pretrained cell models must not be represented as a validated pathogen diagnostic.

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
