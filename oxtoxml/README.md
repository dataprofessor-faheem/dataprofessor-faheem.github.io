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
## October 20, 2026: Research insight interface v0.4

Additional interactive panels have been deployed: RDKit molecular-weight/logP/TPSA distributions, closest within-panel fingerprint analogues, contextual tool-capability comparison (SwissADME / ProTox 3.0 / ADMETlab 3.0), and the prespecified methodological requirements for an endpoint-matched benchmark. These are descriptive capabilities; the server does not expose trained Tox21 or ClinTox model probabilities. Operational validation (JavaScript syntax, public home page, service health, 5/7/15 reference molecular sets, PDF generation) passed in [GitHub Actions run 39409063389](https://github.com/dataprofessor-faheem/dataprofessor-faheem.github.io/actions/runs/39409063389).

## October 22, 2026: Historical benchmark dashboard v0.5

`benchmark.html` displays aggregate, independently rechecked ORIGINAL scaffold-test metrics and retrospective screening budget analyses from the OxToxML research study. `benchmark-data.json` publishes aggregate rows for the six endpoints (4,891 historical labeled test predictions underlying the summaries); it does not publish restricted raw datasets, trained bundles, or private prediction rows. Thirty original numerical metric values were independently reproduced; scaffold identifiers did not overlap between the research data splits. This is not independently sourced external predictive validation. The new dashboard reports sample sizes, class prevalence, ROC-AUC, AP, balanced accuracy, MCC, Brier, reported confidence intervals, and exploratory top-5%, top-10%, and top-20% prioritization outcomes.

The 210/210 molecular field checks and 45/45 nearest-neighbor matches are checks of a separately SAVED 15-structure output snapshot, not a production server accuracy benchmark. A local median RDKit runtime of 14.19 ms across 30 repetitions does not include HTTP, third-party predictors or browser latency.

**Critical boundary:** the public portal remains structure-only; it has no deployed trained Tox21 or ClinTox toxicity-prediction service. The current dashboard must not be described as live six-endpoint inference, independent external toxicity validation or proof of superiority to SwissADME / ProTox 3.0 / ADMETlab 3.0.
