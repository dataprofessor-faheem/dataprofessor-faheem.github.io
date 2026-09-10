# JBR Supabase backend starter

This directory contains a starter PostgreSQL schema for the production phase of the JBR portal.

## What it covers

- researcher profiles and expertise
- research idea submissions
- discovery challenges
- collaborator applications
- projects and project membership
- milestones
- basic audit events
- row-level security enabled on sensitive tables

## Before production activation

1. Create a dedicated JBR Supabase project under an organizational account.
2. Run `schema.sql` in the Supabase SQL editor.
3. Define production roles: public visitor, researcher, verified researcher, project lead, reviewer, data steward, administrator.
4. Add explicit Row Level Security policies for each role.
5. Configure Auth and approved redirect URLs for the final JBR domain.
6. Add storage buckets with separate public and private research-file policies.
7. Create a secure admin workflow for researcher verification and challenge approval.
8. Connect the frontend through environment/config values. Never commit service-role keys to GitHub.
9. Complete privacy, research integrity, authorship, ethics and data-governance policies before collecting sensitive research data.

## Security rule

Only the Supabase public/anonymous key may ever be exposed in a browser frontend, and only with restrictive RLS policies. The service-role key must remain server-side and must never be committed to this repository.
