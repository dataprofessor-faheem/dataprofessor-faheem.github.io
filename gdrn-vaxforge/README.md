# GDRN-VaxForge · GDRN research workbench (v0.2.0)

This isolated directory contains the browser workbench at `/gdrn-vaxforge/`. It does **not** modify the GDR Network homepage, custom-domain settings or DNS.

## What runs in the hosted browser workbench

- Local FASTA validation for protein, DNA and RNA inputs.
- Descriptive QC: sequence counts, duplicate sequences, lengths and gap count.
- Per-position consensus, residue conservation, Shannon entropy and gap frequency for **user-verified aligned** sequences.
- Interactive conservation profile and downloadable JSON/CSV reports.
- All pasted/uploaded FASTA data stay in the browser (no network submission).

## Separate Python research-core release (v0.2.0)

A tested Python source archive was produced separately for the project's development workflow, with modules for (1) explicit NCBI/UniProt public accession retrieval and SHA-256 provenance, (2) QC → user-provided MSA or optional MAFFT → conservation, (3) *unsubmitted* IEDB NextGen MHC-I request construction, and (4) labeled paired model comparison with group bootstrap and permutation testing.

The archive includes CLI, scientific documentation, tests, and synthetic examples. **That entire Python archive is not currently mirrored in this GitHub Pages repository and does not run on GitHub Pages.**

## Stage 2 verification and scientific limitations

- Python automated checks: **11/11 passed** in the development environment.
- Browser: HTML/JS checks and local functional tests with toy protein, DNA and RNA inputs passed.
- Network retrieval: HTTP calls were mocked in tests; real API interoperability was not tested in the restricted environment.
- Benchmark example: synthetic data for engineering demonstration only; not evidence of diagnostic, antigenic, immunogenic or vaccine-protection performance.
- Disease-specific pan-genome software and external epitope predictors are **not yet connected or validated**.

[Read Stage 2 release notes](./RELEASE_v0.2.md) · [Original study](https://doi.org/10.3390/vaccines11061090)

**Production priorities:** verify hosted deployment; connect authorized public data APIs; run real versioned alignment; acquire independent experimental benchmark datasets; audit third-party licenses; then build authenticated compute services. Never commit or upload private patient, unpublished or embargoed datasets to a public site.
