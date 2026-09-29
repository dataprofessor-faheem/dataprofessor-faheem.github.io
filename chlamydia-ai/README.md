# Chlamydia AI MathFusion

Research prototype for AI-assisted Chlamydia inclusion-body analysis in Giemsa and DFA/fluorescence microscopy.

## Hosting

This project is stored in `chlamydia-ai/` inside the GitHub Pages repository.

Target public path:
`https://www.gdrnetwork.org/chlamydia-ai/`

The repository uses the standard GitHub Actions Pages workflow in `.github/workflows/pages.yml`.

## Scientific status

The web interface is a research/demo interface. Chlamydia-specific inference remains disabled until a Chlamydia-labelled model has been trained and independently validated.

## Architecture

Teacher stack:
- CellSAM
- Cellpose-SAM / CPDINO
- micro-SAM
- StarDist

Deployable student:
- YOLO26-seg after Chlamydia-specific fine-tuning/distillation

Mathematical layer:
- calibrated teacher weighting
- Focal-Tversky + Dice
- boundary and signed-distance geometry
- knowledge distillation
- Giemsa/DFA consistency
- calibration and uncertainty-aware review

## Leakage rule

Split by experiment / plate / well / biological replicate. Never split random crops from the same field across train and test sets.
