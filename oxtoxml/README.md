# OxToxML — GDR Network public research portal

**Live website:** https://www.gdrnetwork.org/oxtoxml/

**RDKit scientific analysis service:** https://oxtoxml-gdrn-portal.vercel.app/

**Related original computational research:** https://github.com/drfaheem-007/OxToxML

This directory contains the independent GitHub Pages presentation layer of the OxToxML molecular research portal. GitHub Pages deploys it automatically with the existing network website workflow. The browser retrieves sample molecular structures from a Vercel-hosted FastAPI/RDKit service, submits analyses to it, and exports CSV/JSON/PDF.

The deployed Vercel backend is independent from the original research repository and is not yet Git-synced.

## Scientific scope

- Three example panels: 5, 7 and 15 ordinary molecule structures, NOT measured toxicity datasets.
- Input: SMILES and name; optional text/CSV import.
- Genuine structure calculations: MW, logP, TPSA, QED, hydrogen bonds, Murcko scaffold, Morgan fingerprint (radius 2, 2048 bits), Tanimoto similarity, Butina clustering, fingerprint PCA.
- Outputs: molecular CSV/JSON, reproducibility SHA-256, descriptor PDF report.
- No deployed OxToxML Tox21/ClinTox trained prediction bundles. Do not interpret descriptors or PAINS alerts as chemical toxicity or safety decisions.

## Validation

The repository GitHub Actions workflow at .github/workflows/oxtoxml-smoke.yml checks the live GDR Network webpage, API health, 5/7/15 molecule structural analyses and downloadable PDF.

## Maintenance

Keep the original GDR Network homepage, DNS and other applications unchanged. Review and version-control backend source before making changes to its computational algorithms.