# GDR Custom Domain Launch Plan

## Target production domain

Primary public domain: `www.gdrnetwork.org`
Apex domain: `gdrnetwork.org`
Current GitHub Pages origin: `dataprofessor-faheem.github.io`

## Launch principle

Use `www.gdrnetwork.org` as the canonical public address and configure `gdrnetwork.org` as the apex variant. GitHub Pages can redirect between the apex and `www` variant once both DNS configurations are correct.

## GoDaddy DNS records

After `gdrnetwork.org` is successfully purchased and visible in the GoDaddy account, open the domain DNS management page and configure:

### WWW

| Type | Name | Value | TTL |
|---|---|---|---|
| CNAME | `www` | `dataprofessor-faheem.github.io` | Default / 1 hour |

### Apex / root domain

Create these four A records:

| Type | Name | Value | TTL |
|---|---|---|---|
| A | `@` | `185.199.108.153` | Default / 1 hour |
| A | `@` | `185.199.109.153` | Default / 1 hour |
| A | `@` | `185.199.110.153` | Default / 1 hour |
| A | `@` | `185.199.111.153` | Default / 1 hour |

Optional IPv6 AAAA records supported by GitHub Pages:

- `2606:50c0:8000::153`
- `2606:50c0:8001::153`
- `2606:50c0:8002::153`
- `2606:50c0:8003::153`

Do not use wildcard records such as `*.gdrnetwork.org` for the GitHub Pages deployment.

## GitHub Pages activation

Only after the domain has been purchased and DNS records have been entered:

1. Open the repository `dataprofessor-faheem/dataprofessor-faheem.github.io`.
2. Open **Settings → Pages**.
3. Set **Custom domain** to `www.gdrnetwork.org`.
4. Save and allow GitHub to perform the DNS check.
5. After the certificate becomes available, enable **Enforce HTTPS**.
6. Keep the repository `CNAME` file equal to `www.gdrnetwork.org`.

## Pre-launch checks

- `www.gdrnetwork.org` resolves to `dataprofessor-faheem.github.io`.
- `gdrnetwork.org` resolves to GitHub Pages A records.
- HTTPS certificate is issued.
- Homepage loads at the domain root.
- GDR logo and founder images load correctly.
- Researcher Portal opens.
- Projects workspace opens.
- Founder/Admin console opens.
- No mixed HTTP/HTTPS assets.

## Current migration status

- GDR website: built.
- GDR promoted to GitHub Pages root: completed.
- Previous Research & Data Portal: backed up as `research-portal-legacy.html`.
- Domain purchase: pending registrar checkout.
- GoDaddy DNS: pending purchase.
- GitHub custom-domain activation: pending successful DNS configuration.
- HTTPS enforcement: pending GitHub certificate issuance.

## Production URL goal

`https://www.gdrnetwork.org/`
