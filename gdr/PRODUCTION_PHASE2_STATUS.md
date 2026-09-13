# GDR Production Phase 2 — Status & Activation Runbook

## Public Production Domain
- https://www.gdrnetwork.org/
- GitHub Pages custom domain configured through repository CNAME.

## Completed in Repository

### 1. Production configuration
- Custom production domain recorded in `gdr/config.js`.
- Browser configuration contains no passwords, service-role keys, or mail API secrets.

### 2. Researcher authentication bridge
- Supabase-compatible sign-up, sign-in, sign-out and session handling.
- Researcher profiles sync to PostgreSQL after backend activation.
- Public forms retain local fallback until shared backend is active.

### 3. Founder/Admin security
- Admin console no longer acts as an open browser-local dashboard.
- It stays locked while production backend is disabled.
- When enabled, access requires authenticated Supabase session plus `founder` or `admin` role in `profiles.role`.
- No admin password is hard-coded in GitHub.

### 4. Database registry
Base schema registers:
- researcher profiles
- research ideas
- Discovery Challenges
- collaboration applications
- projects
- project members
- milestones
- audit events

Production Phase 2 migration additionally registers:
- datasets
- dataset versions
- SHA-256 checksums
- provenance and access level
- research outputs
- email events
- organization/admin settings

### 5. Role-based security
- PostgreSQL Row Level Security policies control profile, proposal, challenge, project, membership, milestone, dataset and output access.
- Founder/Admin authorization is database role based.
- Sensitive server keys are never sent to the browser.

### 6. Dataset registration
Founder/Admin Console includes a production dataset registration form for:
- dataset code
- title
- description
- access level
- version
- SHA-256 checksum

### 7. Project registration
Founder/Admin Console includes project registration for:
- project code
- title
- lifecycle status

### 8. Research-idea screening
Founder/Admin dashboard can load real submitted ideas after backend activation and update screening status to:
- approved
- screening
- needs revision
- rejected

### 9. Transactional email
Prepared Supabase Edge Function: `send-gdr-email`.
Supports templates for:
- research idea received
- collaboration application received
- admin alert
- submission status update

Email provider credentials must be stored only as server-side Edge Function secrets.

### 10. Production path repair
- Landing page challenge data now loads from `/gdr/data/challenges.json` so it works from the custom-domain root.
- Landing page dynamically loads the Supabase client, public config and backend bridge.
- Idea and collaboration forms can switch automatically from browser-local fallback to shared database mode once Supabase is activated.

## External Activation Required

### A. Supabase
Connect/create a dedicated GDR Supabase project, then:
1. Apply `gdr/supabase/schema.sql`.
2. Apply `gdr/supabase/production_phase2.sql`.
3. Configure Authentication email/password provider.
4. Set Site URL to `https://www.gdrnetwork.org/`.
5. Add redirect URL `https://www.gdrnetwork.org/gdr/portal/`.
6. Create the founder user account through Auth.
7. Create/update founder profile with role = `founder` through a trusted admin/server-side process.
8. Put only the Supabase project URL and publishable/anon key into `gdr/config.js`.
9. Set `backendEnabled: true`.
10. Deploy the `send-gdr-email` Edge Function.

### B. Resend / transactional mail
1. Connect the Resend service.
2. Add and verify `gdrnetwork.org` as a sending domain.
3. Add the DNS records Resend provides (SPF/DKIM) in GoDaddy.
4. Create sender such as `notifications@gdrnetwork.org`.
5. Store `RESEND_API_KEY`, `GDR_FROM_EMAIL`, and `GDR_ADMIN_EMAIL` as Supabase Edge Function secrets.
6. Send a test email and verify delivery/logging.

## Final Acceptance Test
The platform is production-ready only when all items below pass:
- public homepage loads through HTTPS
- GDR logo and both founder photos load
- challenge cards load
- Researcher Portal account creation works
- confirmation email works if enabled
- researcher sign-in works
- researcher profile persists after browser/device change
- research idea writes to PostgreSQL
- collaboration application writes to PostgreSQL
- non-admin user cannot enter `/gdr/admin/`
- founder/admin user can enter `/gdr/admin/`
- founder dashboard counts real records
- idea status updates persist
- project registration persists
- dataset registration persists
- SHA-256 field persists
- email notification sends and email event is logged
- logout removes admin access
- no secrets are present in public GitHub source

## Security Rule
Never store admin passwords, Supabase service-role keys, Resend API keys, private datasets, patient identifiers, confidential manuscripts, or unpublished sensitive research files in the public GitHub Pages repository.
