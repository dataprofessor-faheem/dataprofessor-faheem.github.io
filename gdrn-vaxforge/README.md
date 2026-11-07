# GDRN-VaxForge — live browser sequence workbench v0.3.0

GDRN-VaxForge is an open, local-first research interface at `/gdrn-vaxforge/` on the GDRN static portal.

## Implemented now

- Manual and local file FASTA import for **protein, DNA and RNA**, with alphabet validation and deduplication counts.
- Optional on-demand public UniProtKB FASTA retrieval via `rest.uniprot.org`. Subject to network and CORS access.
- User-supplied **verified MSA** conservation: per-site consensus, modal fraction, occupancy, Shannon entropy and variant counts.
- Conserved-window **exploration** with configurable thresholds. These are not predicted epitopes.
- Pairwise identity where input size permits. No-gap overlap is the denominator.
- Full reproducibility JSON with method versions and SHA-256 of the input (if WebCrypto available).
- Column-level and window-level CSV export.
- Comprehensive browser-core tests run in GitHub Actions.
- New navigation entry from the existing GDR researcher portal. No authentication logic or DNS settings were changed.

**Processing limit:** 500 sequences and 3,000,000 total sequence characters. Pairwise calculations capped at 24 sequences x 15,000 aligned positions.

## Limitations and interpretation

The browser does **not** perform sequence alignment or full bacterial/viral pan-genome analysis. Equal-length FASTA records alone do not prove a valid multiple sequence alignment. Current analyses are descriptive, not statistical significance tests. No antigen target selection, B-/T-cell epitope predictions, vaccine constructs, immune response, toxicity or efficacy are calculated. Clinical efficacy and immune protection require appropriate independent experimental evidence.

The browser does not upload user FASTA data to GDRN. Public UniProt retrieval transmits the accession only to the third-party API. Do not paste confidential, patient-identifying or embargoed sequences into an unaudited third-party tool.

## Sequential roadmap

1. Public accession QC, provenance and data normalization — browser import and separate research-core adapters.
2. Verified MSA using MAFFT or another controlled alignment backend — pending.
3. Disease-specific pan-genome/pan-proteome analysis — pending.
4. Evidence-based B-cell, MHC-I and MHC-II prediction via authorized software/API — pending.
5. Independent experimental datasets, homology-aware benchmarking, confidence intervals and bias assessment — pending.
6. Construct-type-specific safety and scientific review — pending.

[Public methods reference](https://doi.org/10.3390/vaccines11061090) · [Pipeline manifest](./pipeline-manifest.json)

This is an analysis-ready **sequence exploration module**; it is not an end-to-end vaccine engineering engine.
