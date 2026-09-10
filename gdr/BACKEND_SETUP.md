# GDR Shared Backend Activation

## Current status

The GDR frontend, Researcher Portal, Founder/Admin preview, database schema, authentication bridge, and local fallback are in the repository.

The shared backend becomes active after a dedicated Supabase project is created and its **Project URL** plus **Publishable/Anon key** are inserted into `gdr/config.js`.

## Activation sequence

1. Create a dedicated Supabase project for GDR.
2. Open the SQL Editor in Supabase.
3. Run `gdr/supabase/schema.sql`.
4. In Supabase Authentication, enable Email/Password authentication.
5. Set the Site URL to `https://dataprofessor-faheem.github.io/gdr/`.
6. Add `https://dataprofessor-faheem.github.io/gdr/portal/` as an allowed redirect URL if confirmation or password-reset flows use redirects.
7. Copy the Supabase **Project URL**.
8. Copy the browser-safe **Publishable key** (or legacy anon key if that is what the project exposes).
9. Edit `gdr/config.js`:

```js
window.GDR_CONFIG = {
  supabaseUrl: 'YOUR_PROJECT_URL',
  supabasePublishableKey: 'YOUR_PUBLIC_KEY',
  backendEnabled: true,
  siteUrl: 'https://dataprofessor-faheem.github.io/gdr/'
};
```

10. Test account creation in `/gdr/portal/`.
11. Confirm email if email confirmation is enabled.
12. Sign in and save a researcher profile.
13. Verify the record appears in the `profiles` table.
14. Submit a research idea and verify it appears in `research_ideas`.
15. Assign `founder` roles only through a trusted Supabase/admin process after confirming the founders' authenticated user IDs.

## Critical security rules

- NEVER put a Supabase `service_role` key in GitHub Pages, JavaScript, HTML, or any public repository file.
- Keep Row Level Security enabled.
- Founder/admin roles must not be self-assignable by researchers.
- Do not expose private research ideas publicly.
- Do not put confidential research datasets in GitHub Pages.
- Human/clinical/identifiable data require an approved secure data-governance environment beyond a public static host.
- Review privacy, ethics, intellectual-property, data-retention, authorship, and incident-response policies before broad public launch.

## Architecture after activation

Public GDR Site
→ Supabase Auth
→ Researcher Profile
→ Research Idea Submission
→ RLS-protected PostgreSQL records
→ Founder/Admin review
→ Challenge recruitment
→ Project team
→ Private project workspace (future release)

## Current limitation

The repository cannot create the user's Supabase account/project or obtain its project credentials automatically. Until the Project URL and public key are supplied, the website intentionally remains in local fallback mode rather than pretending a central database is active.
