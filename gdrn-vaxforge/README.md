# GDRN-VaxForge · hosted sequence research prototype (v0.1)

This isolated directory provides the browser-only demo at `/gdrn-vaxforge/`.

## Implemented in the hosted browser demo

- Input and validate protein FASTA data (no external file transfer).
- Perform basic sequence QC: record count, identical sequence count, lengths and gap count.
- Calculate descriptive per-position conservation for a **user-verified, already aligned** MSA.
- Download results as JSON.

This website does **not** retrieve external sequences, construct an alignment, predict B/T-cell epitopes, design vaccines, or demonstrate efficacy. The full experimental Python research-core package (including unit tests, benchmark metrics, tool registry, documentation and synthetic examples) was prepared separately and delivered with the research review; it is not yet contained in this GitHub Pages subdirectory.

## Next integration milestones

1. Reproducible reference sequence ingestion, accession manifest and approved MSA adapter.
2. Branch-aware pathogen and cancer inputs; version-controlled tool manifests.
3. Authorized IEDB next-generation API adapter with async job status, no website scraping.
4. Independent experimental benchmark datasets, leakage audit, uncertainty and HPC cost profiles.
5. Secure compute backend for private research files; never upload sensitive files to public Pages.

**Scientific basis**: Khamjan et al. *Vaccines* 2023;11(6):1090. https://doi.org/10.3390/vaccines11061090

**Important**: Model predictions and conservation scores are neither proof of natural immunogenicity nor evidence of protective vaccine efficacy. License terms of each third-party software component must be reviewed prior to integration, especially in commercial contexts.
