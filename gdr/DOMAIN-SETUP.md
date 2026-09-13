# GDR Custom Domain Setup Guide

## Goal
Replace the public GitHub Pages address with a professional domain you own while keeping GitHub Pages as the host.

Current site:
`https://dataprofessor-faheem.github.io/gdr/`

Target example:
`https://www.gdrresearch.org/`

> Do not create the final `CNAME` file until the exact purchased domain is confirmed.

## Recommended domain pattern
Prefer a short, credible research-oriented domain such as:

- `gdrresearch.org`
- `gdrnetwork.org`
- `gdrdiscovery.org`
- `globaldiscoveryresearch.org`

Availability must be checked at the registrar before purchase.

## Recommended production arrangement
For the current GitHub user-site repository, the custom domain is attached to the GitHub Pages site. GDR currently lives under `/gdr/`.

For the first custom-domain release, configure the domain at the GitHub Pages level and keep the existing `/gdr/` application paths stable. Once the domain is active, the public GDR entry point can be promoted to the root in a controlled migration.

## DNS records for an apex/root domain
If the purchased domain is `example.org`, create these DNS records:

| Type | Host | Value |
|---|---|---|
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| CNAME | www | dataprofessor-faheem.github.io |

Use the exact values shown by GitHub documentation if GitHub changes them in the future.

## GitHub Pages settings
After DNS records are saved:

1. Open the repository `dataprofessor-faheem/dataprofessor-faheem.github.io`.
2. Open **Settings**.
3. Open **Pages**.
4. Under **Custom domain**, enter the purchased domain, preferably `www.example.org` or the apex domain according to the chosen DNS plan.
5. Save.
6. Wait for the DNS check to pass.
7. Enable **Enforce HTTPS** when available.

## Domain verification
For stronger protection against domain takeover, verify the domain in GitHub account settings before or during the Pages setup.

GitHub will give a TXT record similar to:

`_github-pages-challenge-dataprofessor-faheem.example.org`

Copy the TXT host and TXT value exactly into the registrar DNS panel, then verify it in GitHub.

## Final repository file
Once the exact purchased domain is confirmed, add a root-level `CNAME` file containing only the domain, for example:

```
www.example.org
```

Do not put `https://`, paths, spaces, or extra text in the `CNAME` file.

## Security checklist

- Turn on registrar account 2FA.
- Keep WHOIS privacy enabled when supported.
- Turn on auto-renew.
- Use a unique registrar password.
- Enable GitHub 2FA.
- Verify the domain in GitHub.
- Enable HTTPS on GitHub Pages.
- Use DNSSEC if the registrar supports it and it is compatible with the chosen DNS setup.
- Never commit registrar passwords, API keys, Supabase service-role keys, private certificates, or recovery codes to this public repository.

## After purchase
Send the exact purchased domain name to the project maintainer. The remaining tasks are:

1. add/update the `CNAME` file;
2. update canonical/OG URLs;
3. update any absolute public URLs;
4. test root and `www` redirects;
5. verify HTTPS;
6. update README and production documentation.
