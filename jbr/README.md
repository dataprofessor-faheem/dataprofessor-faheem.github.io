# JBR Global Discovery & Research Network

A GitHub Pages MVP for an international multidisciplinary research-discovery and collaboration platform.

**Founders**
- Dr. Mohd Faheem Khan, PhD — AI & Machine Learning, Biotechnology, Bioinformatics
- Dr. Khurshid Ahmad, PhD — Drug Discovery, Health Informatics, Bioinformatics

## Live route

When GitHub Pages is serving the repository root, this project is available at:

`https://dataprofessor-faheem.github.io/jbr/`

## Current MVP

The live static MVP includes:

- professional responsive institutional landing page
- JBR Discovery Challenge cards
- live client-side challenge search and status filtering
- research-domain architecture
- discovery workflow
- founder profiles
- research-idea form
- browser-local draft persistence
- JSON export of submitted research-idea drafts
- challenge expression-of-interest form
- browser-local expression-of-interest persistence
- prepared PostgreSQL/Supabase schema for the production multi-user phase

## Important limitation of GitHub Pages

GitHub Pages is static hosting. It cannot by itself provide secure multi-user authentication, a shared database, private project workspaces or confidential research-data storage.

The MVP therefore uses browser `localStorage` only for form demonstrations and draft capture. Do not treat locally saved submissions as received by JBR.

The `/supabase` directory contains the starter backend schema required for the next production phase.

## Architecture

```text
jbr/
├── index.html
├── manifest.webmanifest
├── assets/
│   ├── app.js
│   ├── logo.svg
│   └── styles.css
├── data/
│   ├── challenges.json
│   └── researchers.json
├── supabase/
│   ├── README.md
│   └── schema.sql
├── PROPOSAL.md
└── DEVELOPMENT_PROGRESS.md
```

## Deployment

Because this is located inside the user GitHub Pages repository, no separate build step is required for the static MVP. Files are served directly from the `jbr/` directory after GitHub Pages publishes the latest commit.

## Production priorities

1. Connect managed authentication and PostgreSQL backend.
2. Add verified researcher profiles and role-based access.
3. Add administrative scientific screening and challenge-approval workflow.
4. Replace local browser forms with shared database submissions.
5. Add private project workspaces and secure document storage.
6. Add governance policies before sensitive data or human-subject information is collected.
7. Add custom domain and organizational GitHub ownership when institutional branding is finalized.
