# GDRN-VaxForge v0.2.0 — Stage 2

**Released:** 2026-11-04  
**Scientific status:** active computational research prototype, not an experimentally validated vaccine platform.

## Changes from v0.1

- Browser interface: protein/DNA/RNA FASTA validation; MSA-aware per-column conservation; residue entropy; CSV/JSON outputs; locally plotted conservation profile.
- Python package (provided separately as the v0.2 source archive in the development conversation): accession-based retrieval adapter for NCBI E-utilities and UniProt REST, with exact accession checks, bounded response and SHA-256 provenance.
- Sequential offline pipeline: user-provided MSA or single-accession retrieval → FASTA QC → descriptive conservation → optional *unsubmitted* IEDB MHC-I request plan.
- Model-comparison engine: paired group-bootstrap 95% interval and group-level permutation test for AUROC or AP on independently labeled observations.
- Validation: **11 of 11 Python tests passed** on the development machine; HTML/JS syntax checks passed. Network acquisition interoperability remains untested due to environment network restrictions.

## Independent benchmarking

A deliberately synthetic example (12 observations, 6 artificial groups) yielded AUROC 0.8889 versus 1.0000, a delta of 0.1111, approximate group bootstrap 95% interval [0, 0.4444], group-swap permutation p ≈ 0.245. **This is not evidence of model superiority, vaccine efficacy or clinical effect.** These figures must not appear as biological findings in a manuscript.

## Complexity

FASTA parsing O(C) over C characters; aligned conservation O(NL) for N records of alignment length L; score sorting O(M log M) on M labeled measurements; group bootstrap O(BM log M) for B replicates; permutation O(PM log M) for P replicates. External MAFFT and third-party model runtimes are excluded.

## Production gates

1. Live NCBI/UniProt API smoke tests under their usage limits and terms; explicit external data transmissions only.
2. Independent homolog/lineage/patient-aware experimental evaluation datasets.
3. Verify IEDB NextGen API schema, versioning, access and license; do not scrape private tools.
4. User authentication, isolated compute, uploads and quotas before processing private data.
5. Independent scientific review; in silico binding and docking cannot establish vaccine safety/protection.

**No GDRN domain/DNS changes were made.** This release page documents the software scope; it does not imply a validated production analysis backend.