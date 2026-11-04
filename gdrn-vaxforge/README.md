# GDRN-VaxForge 0.1.0 — validation-first scientific prototype

**Status: working computational foundation; not an end-to-end vaccine predictor.**

GDRN-VaxForge connects the conceptual stages of the paper: Khamjan et al., *Vaccines* 2023;11(6):1090, DOI: 10.3390/vaccines11061090, to a reproducible modular engineering plan for vaccine informatics.

## What actually runs in v0.1

1. FASTA ingestion and strict molecular alphabet, duplicate-ID and input provenance checks.
2. Per-column residue conservation and entropy **only for scientifically pre-aligned equal-length sequences**. It does not align sequences automatically or predict epitopes.
3. Contiguous consensus-conservation runs, clearly distinguished from predicted epitopes.
4. Model evaluation from supplied **experimentally labeled** data (AUROC, AP, Brier, confusion matrix, MCC) and percentile confidence intervals from independent-group bootstrap.
5. Generate an **unsubmitted** IEDB Next-Generation MHC-I request JSON (no network call).
6. Self-contained privacy-preserving browser demo (`web/index.html`) for QC and descriptive conservation, with downloadable JSON.

**No external prediction, annotation, structure modeling, immunogenicity testing, docking, clinical efficacy assessment, or automatic pan-genome inference has been performed.**

## Installation and smoke test

```bash
python3 -m unittest discover -s tests -v
python3 -m gdrn_vaxforge qc examples/toy_aligned_proteins.fasta --allow-gaps
python3 -m gdrn_vaxforge conservation examples/toy_aligned_proteins.fasta --min-fraction 1 --min-run 3 --out conservation.json
python3 -m gdrn_vaxforge benchmark examples/toy_predictions.csv --bootstrap 200 --out benchmark.json
python3 -m gdrn_vaxforge iedb-plan examples/toy_proteins_ungapped.fasta --out iedb_request_UNSUBMITTED.json
```

Example inputs are **synthetic testing data**. Do not use resulting scores in a publication as biological results.

## Modular strategy

- Pathogen target discovery: input and QC → genome annotation/variants → bacterial pan-genome or viral proteome comparative analysis → curated antigen candidates → epitope prediction and processing → safety/host matching → HLA diversity → construct-specific assessment → independent validation and reproducibility bundle.
- Cancer: paired tumor/normal sequencing and expression/variant interpretation → neoantigen methods (e.g., pVACtools) → tumor-specific filtering → independent evidence, **not pathogen pan-genomics**.
- Other disease areas: require a scientifically defined antigen and disease mechanism. A vaccine is not a general treatment for non-antigen-defined conditions.

External adapters must have version-pinned containers or documented APIs, explicit terms of use and tests. Do not scrape third-party tools.

## External references and legal

- IEDB NextGen API: https://nextgen-tools.iedb.org/docs/api/endpoints/
- IEDB v5.0 release 2026-10-02: https://discuss.iedb.org/t/next-generation-iedb-tools-website-and-api-release-5-0-oct-2-2026/344
- Panaroo: https://github.com/gtonkinhill/panaroo
- PPanGGOLiN: https://github.com/labgem/PPanGGOLiN
- MHCflurry: https://github.com/openvax/mhcflurry
- pVACtools: https://pvactools.readthedocs.io/en/latest/
- BepiPred 3.0: https://services.healthtech.dtu.dk/services/BepiPred-3.0/

The GDRN code here is Apache-2.0; **this does not confer any license for third-party tools, data or model weights**. Check institutional, commercial, data privacy and redistribution permissions for each adapter.

## Security

No FASTA data is transmitted by the browser demo. Server-side production processing will require authentication, rate limits, encrypted private storage, safe file handling, consent/data use checks, incident logging, and separate compute from the public static GitHub Pages site. Do not commit private patient, manuscript, or embargoed data to public GitHub.

## Honest limitations

Computational HLA binding, predicted epitope conservation, or docking does not establish natural processing, immunogenicity, protection, clinical efficacy or safety. Model benchmarking must use independent, leakage-controlled experimental datasets. See `docs/BENCHMARKING.md` and `docs/ARCHITECTURE.md`.