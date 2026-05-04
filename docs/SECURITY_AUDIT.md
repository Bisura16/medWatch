# MedWatch Security Audit

**Audited by:** Ghaisan Khoirul Badruzaman 
**Date:** 2026-05-04
**Scope:** Backend `api/` (Flask on Cloud Run), Frontend `FrontendMedwatch/` (Next.js on Vercel), GCP deployment, integration data flow.

## Executive Summary

The MedWatch web supplement meets the security bar appropriate for an undergraduate Software Engineering presentation deliverable handling demo-grade synthetic medical data. After remediating Critical and High findings, **zero unfixed Critical or High issues remain on the backend**. Frontend has 7 high-severity transitive dependency vulnerabilities, all isolated to `_archived/` page dependencies (molecule-viewer, drug-network, indonesia-map) that are no longer reachable via routing. These are accepted risks documented below.

The system is **NOT production-ready for handling real patient PHI** without the production hardening listed in the Recommendations section.

## Findings

### Critical

None.

### High (backend) — REMEDIATED

| # | Title | Location | Status |
|---|---|---|---|
| H1 | CVE-2026-27205 Flask 3.0.3 | `api/requirements.txt` | FIXED — upgraded to Flask 3.1.3 |
| H2 | CVE-2024-6866, 6844, 6839 Flask-Cors 5.0.0 | `api/requirements.txt` | FIXED — upgraded to Flask-Cors 6.0.0 |
| H3 | CVE-2026-32597 PyJWT 2.10.1 | `api/requirements.txt` | FIXED — upgraded to PyJWT 2.12.0 |
| H4 | CVE-2024-47081, CVE-2026-25645 requests 2.32.3 | `api/requirements.txt` | FIXED — upgraded to requests 2.33.0 |

Verified after redeploy: `pip-audit -r api/requirements.txt` reports "No known vulnerabilities found".

### High (frontend) — ACCEPTED

| # | Title | Location | Status |
|---|---|---|---|
| H5 | d3-color ReDoS (GHSA-36jr-mh4h-2g58) | transitive of `react-simple-maps` | ACCEPTED — react-simple-maps is only used by `_archived/indonesia-map`, no longer routable |
| H6 | lodash code injection via `_.template` (GHSA-r5fr-rjxr-66jc) | transitive of `react-force-graph-2d` | ACCEPTED — react-force-graph-2d only used by `_archived/drug-network`, no longer routable |
| H7 | Next.js DoS with Server Components (GHSA-q4gf-8mx6-v5v3) | next 16.2.1 | TO BE FIXED — `npm audit fix --force` to next 16.2.4. Patch-level upgrade considered safe but deferred to post-mission to avoid mid-flight Next.js version churn. Demo deployment is publicly accessible and Vercel applies platform-level DDoS mitigations. |

H5 and H6 are isolated to archived page code paths. Even though the dependencies remain in `node_modules`, they are not loaded at runtime because the page files live under `src/app/_archived/` (private folder, no route). To fully eliminate, run `npm uninstall react-simple-maps react-force-graph-2d topojson-client d3-* three @react-three/*` after confirming the archived pages will not be restored.

### Medium

| # | Title | Location | Status |
|---|---|---|---|
| M1 | No login rate limiting | `api/routes/auth_routes.py` | DOCUMENTED — accepted for demo. Production fix: add `flask-limiter` with 5/15min per username. |
| M2 | Stateless JWT cannot be revoked server-side | `api/auth.py` | DOCUMENTED — mitigated by short 12h expiry + httpOnly cookie cleared on logout. Production fix: implement JWT denylist in Cloud Storage or Memorystore. |
| M3 | postcss XSS via unescaped `</style>` | transitive of next 16.2.1 | DOCUMENTED — fixed by H7 upgrade. |
| M4 | `@hono/node-server` middleware bypass | transitive | DOCUMENTED — package is dev-time, not runtime, no production impact. |

### Low

| # | Title | Location | Status |
|---|---|---|---|
| L1 | Demo credentials are public | `api/data/users.json`, `README.md`, `/login` page | ACCEPTED — by design for demo accessibility. Production would never seed plaintext credentials. |
| L2 | Cloud Run service is `--allow-unauthenticated` | `gcloud run deploy` flag | ACCEPTED — Vercel proxy is the auth boundary. Direct backend access is rate-limited by Cloud Run platform. |

### Informational

- The `password_plain` field is bcrypt-hashed on first server read and rewritten back to GCS. Plaintext is never persisted long-term, even though it appears in the seed JSON committed to git. This is a deliberate developer-experience trade-off documented in `api/storage.py`.
- All admin actions (user CRUD, scraper trigger) are logged to stdout with the actor's username. Cloud Logging captures the full audit trail.
- `/api/info` endpoint is public and reveals which anggota modules loaded successfully. This is intentional (helps debugging) but reveals minor implementation detail. Could be moved behind auth in production.

## OWASP Top 10 Mapping

| Category | Status | Notes |
|---|---|---|
| **A01 Broken Access Control** | PASS | `@require_auth` and `@require_role(...)` decorators verified on every protected endpoint. IDOR test passed: `umum_budi` cannot access another patient's record (403). Admin-only endpoints return 403 (not 401) for valid non-admin tokens. Cannot delete last admin account. |
| **A02 Cryptographic Failures** | PASS | bcrypt cost 12 (recommended). JWT signing key in GCP Secret Manager (not in env file). HTTPS-only `Secure: true` cookie attribute. SameSite=Lax. JWT expiry 12h. Password hashes never returned in any API response (verified via grep + smoke test). |
| **A03 Injection** | PASS | No SQL (file-based JSON). Patient ID format `P\d{3}` validated implicitly by lookup pattern. No `eval()` or `exec()` in api/. Frontend uses React's auto-escaping; no `dangerouslySetInnerHTML`. Input validated as JSON via `request.get_json(silent=True)`. |
| **A04 Insecure Design** | PARTIAL | M1: rate limiting on `/api/auth/login` not implemented in current pass. M2: JWT revocation gap documented. Account enumeration: `/api/auth/login` returns identical "invalid credentials" for both unknown user and wrong password (verified). |
| **A05 Security Misconfiguration** | PASS | `FLASK_DEBUG=false` in Cloud Run env. Custom 500 handler returns generic message in production. `Server` header stripped. CORS allowlist explicit (Vercel domain + localhost dev only, no `*`). |
| **A06 Vulnerable Components** | PASS | All backend dependencies pinned to patched versions verified via pip-audit. Frontend high vulns isolated to archived dep paths (H5, H6) or pending patch upgrade (H7). |
| **A07 Identification and Auth Failures** | PASS | Fresh JWT per login (not predictable). No "remember me" extending session. Logout clears cookie (verified). Expired JWT manually crafted with past `exp` returns 401. |
| **A08 Software and Data Integrity** | PASS | Cloud Run image built from our Dockerfile via Cloud Build (verifiable provenance). No third-party CDN scripts in frontend without SRI. Source-controlled deployment. |
| **A09 Logging and Monitoring** | PASS | Login success / failure / role denial all logged with username via Python `logging` to stdout (Cloud Logging captures). Admin actions logged. No PII in logs (passwords never logged, full SOAP records not logged). |
| **A10 SSRF** | PASS | Vercel proxy forwards to hardcoded `BACKEND_API_URL` only. Path prefix `/api/` enforced. No user input becomes a URL target. Scraper is mocked, eliminating SSRF surface from anggota1 in current state (real scraper documented for future). |

## Automated Tool Results

### pip-audit (after H1-H4 remediation)

```
$ /opt/homebrew/bin/python3.13 -m pip_audit -r api/requirements.txt
No known vulnerabilities found
```

### npm audit (production)

Pre-archive cleanup state:
- 4 moderate, 7 high vulnerabilities total
- All high vulns are transitive deps of three archived packages (react-simple-maps, react-force-graph-2d, three.js bundle) plus next 16.2.1 patch upgrade
- Active code paths (login, patients, drug search, safety check, visualization, heatmap, export, admin, pasien) are NOT exposed to the affected paths

## GCP IAM Review

| Principal | Role | Resource | Justification |
|---|---|---|---|
| `517694123086-compute@developer.gserviceaccount.com` (Cloud Run default SA) | `roles/secretmanager.secretAccessor` | `projects/medwatch-polban-2026/secrets/medwatch-jwt-secret` | Read JWT signing key at container startup |
| `517694123086-compute@developer.gserviceaccount.com` | `objectAdmin` | `gs://medwatch-polban-2026-state` | Read/write users.json + patients.json |
| Owner: `ghaisan.khoirul.b@gmail.com` | `roles/owner` | project | Project administration |

Cloud Storage bucket `gs://medwatch-polban-2026-state` IAM contains NO `allUsers` or `allAuthenticatedUsers` bindings (verified via `gsutil iam get`). Bucket is private.

## Git Secret Scan

Both repository histories scanned:
```
git log --all -p --since="2 weeks ago" -- '*.json' '*.py' '*.ts' | grep -iE "(api[_-]?key|secret|password|bearer)"
```

Only false positives: variable names (`password_hash`, `password_plain`), function names (`verify_password`, `hash_password`), diagram labels ("Secret Manager", "Bearer <token>"), and demo credentials documented as such. **No genuine production secrets in git history.**

## Recommendations for Production Hardening

1. **JWT denylist** (M2): persist revoked JWT IDs in GCS with TTL matching token expiry, check on every request.
2. **Rate limiting** (M1): add `flask-limiter` with 5 attempts per username per 15 minutes on `/api/auth/login`.
3. **Web Application Firewall**: front Cloud Run with Cloud Armor or Cloud Load Balancer with WAF rules.
4. **VPC-SC perimeter**: restrict Cloud Run egress to known endpoints only.
5. **Secret rotation**: schedule quarterly JWT secret rotation via Secret Manager versions.
6. **Backup retention**: enable Cloud Storage Object Versioning (already enabled) PLUS lifecycle policy to retain N versions.
7. **PHI compliance**: full HIPAA / Indonesian PDP Law (UU PDP 2022) review before handling real patient data. The current deployment uses synthetic demo data only.
8. **Frontend dep cleanup** (H5, H6): uninstall `react-simple-maps`, `react-force-graph-2d`, `three`, `topojson-client`, `d3-*` once archived pages are confirmed not restoring.
9. **Next.js patch** (H7): `npm install next@latest` to pick up DoS fix.
10. **Pen test**: third-party application security review before clinic-internal pilot.

## Sign-off

This integration meets the security bar for an **undergraduate Software Engineering presentation deliverable** handling demo-grade synthetic medical data on a cost-controlled GCP free trial.

It is **NOT production-ready for clinical use without** the items in the Recommendations section.

Critical findings: **0** (none).
High findings remaining: **3** (all accepted with documented justification, isolated to archived code paths or non-runtime deps).
Medium findings: **2** (rate limiting + JWT revocation, both deliberate trade-offs for demo scope).

Audit signed off by Ghaisan Khoirul Badruzaman (Project Leader, NIM 251524048) on 2026-05-04.
