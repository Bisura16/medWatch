# Wave 0 Scout Findings

Mission: medwatch-windows-installers-2026-05-25
Subagent: scout
Date: 2026-05-25
Mode: read-only recon
Host: macOS Darwin 25.3.0
Working dirs:
- Backend: /Users/ghaisan/Documents/MedWatchIntegration/medWatch
- Frontend: /Users/ghaisan/Documents/MedWatchIntegration/FrontendMedwatch (symlink to /Users/ghaisan/Documents/FrontendMedWatch)

All file:line citations are absolute. UNVERIFIED is used wherever a claim could not be confirmed in this session.

---

## 1. Backend Flask layout

### 1.1 Entry point and factory

The Flask application is built by `create_app()` in api/app.py:36 and exposed both as the factory and as a module-level `app` instance at api/app.py:89. The module manipulates `sys.path` at api/app.py:18 so that `from api.config import ...` works under both gunicorn and `flask run` invocations. Logging is configured at INFO level at api/app.py:29.

Inside `create_app()`:
- Static folder is wired to `api/static/` at api/app.py:47.
- CORS is initialised with the allowlist `CORS_ORIGINS` (api/app.py:49 and api/config.py:28).
- Eight blueprints are registered between api/app.py:55 and api/app.py:62 (health, auth_routes, patient_routes, drug_routes, safety_routes, visualization_routes, pdf_routes, admin_routes).
- A static landing route `/` returns `api/static/index.html` at api/app.py:64.
- JSON 404 and 500 error handlers are installed at api/app.py:69 and api/app.py:74.
- An `after_request` hook removes the `Server` header at api/app.py:80.

Local dev launch path: `app.run(host="0.0.0.0", port=PORT, debug=DEBUG)` at api/app.py:92.

### 1.2 Configuration knobs

All config lives in api/config.py and is read from `os.environ` only at import time (no disk or network side effects).

- `BASE_DIR`, `API_DIR`, `DATA_DIR` (api/config.py:12).
- `ANGGOTA_DIRS` dict mapping each anggota namespace to its filesystem path (api/config.py:16).
- `JWT_SECRET` defaulting to `dev-only-do-not-use-in-prod` (api/config.py:24); algorithm `HS256` and expiry of 12 hours.
- `CORS_ORIGINS` is hardcoded to three entries: `https://medwatch-frontend.vercel.app`, `http://localhost:3000`, `http://localhost:5173` (api/config.py:28 to api/config.py:32). Note: not env-driven despite the `.env.example` hint at .env.example:12.
- `GCP_PROJECT_ID`, `GCS_BUCKET`, `USE_CLOUD_STORAGE` (api/config.py:34 to api/config.py:36).
- `OPENFDA_API_KEY` read from env with empty-string fallback (api/config.py:41).
- `PORT = int(os.environ.get("PORT", 8080))` at api/config.py:43.
- `DEBUG` toggled by `FLASK_DEBUG` env var (api/config.py:44).

### 1.3 Auth primitives and middleware

api/auth.py:14 hashes passwords with bcrypt cost factor 12.
api/auth.py:44 issues HS256 JWTs with claims `sub`, `role`, `name`, `iat`, `exp`, `iss="medwatch-api"`.
api/auth.py:69 verifies tokens and returns `None` on any `PyJWTError`.

api/middleware.py:29 `require_auth` decorator extracts the bearer token, calls `verify_token`, and attaches `flask.g.user` with keys `username`, `role`, `name`.
api/middleware.py:63 `require_role(*allowed_roles)` factory composes on top of `require_auth`; logs denial reasons including username and required role list.

### 1.4 Storage abstraction

api/storage.py provides a uniform load/save interface that flips between Google Cloud Storage and local JSON under `api/data/` based on `USE_CLOUD_STORAGE` (api/storage.py:79 `_load`, api/storage.py:100 `_save`).
- GCS client is lazily imported in `_gcs()` at api/storage.py:28 so importing this module is free when GCS is disabled.
- `load_users()` (api/storage.py:119) auto-hashes any `password_plain` fields it finds and persists back.
- `load_patients()`/`save_patients()` (api/storage.py:141, api/storage.py:152) use the `patients.json` key.

For desktop offline mode the local-disk branch (`_load_local`, `_save_local`) is the only relevant code path.

### 1.5 Helpers

api/helpers.py:16 `ok()` returns Flask `(jsonify(data), status)` tuples.
api/helpers.py:32 `err()` does the same for error payloads with optional `**extra` merge.
api/helpers.py:51 `strip_password_fields()` drops `password_hash`, `password_plain`, `password`.
api/helpers.py:92 `parse_resep_to_meds()` parses free-form bidan resep strings into clean drug-name lists. Has its own regex constants at api/helpers.py:70 and api/helpers.py:86.

### 1.6 Bootstrap (anggota module loader)

api/bootstrap.py:24 `_inject_paths()` prepends each existing anggota directory to `sys.path`.
api/bootstrap.py:33 `get_module(anggota, module_name)` lazy-loads and caches modules; failures are sticky (cached as `None`) so broken imports do not retry every request. Critical for desktop bundling because `anggota3/BacaData.py` has a known SyntaxError and must not crash the app (see api/routes/visualization_routes.py:5).

### 1.7 Routes enumeration

Eight blueprints under api/routes/ are registered. For each I list its name, the url_prefix (none of them set one; everything is under `/api/...`), and every route.

#### health.py (blueprint `health`)

api/routes/health.py:15 Blueprint declared; no url_prefix.

| Method | Path | View | Purpose |
|---|---|---|---|
| GET | /api/health | `health` (api/routes/health.py:19) | Liveness probe returning status, version, ISO timestamp |
| GET | /api/info | `info` (api/routes/health.py:34) | Reports which anggota modules loaded plus GCP context |

#### auth_routes.py (blueprint `auth_routes`)

api/routes/auth_routes.py:16 Blueprint declared.

| Method | Path | View | Purpose |
|---|---|---|---|
| POST | /api/auth/login | `login` (api/routes/auth_routes.py:20) | Verify credentials and issue JWT |
| GET | /api/auth/me | `me` (api/routes/auth_routes.py:60) | Return identity from bearer token |
| POST | /api/auth/logout | `logout` (api/routes/auth_routes.py:71) | Acknowledge logout (stateless) |

#### patient_routes.py (blueprint `patient_routes`)

api/routes/patient_routes.py:22 Blueprint declared.

| Method | Path | View | Purpose |
|---|---|---|---|
| GET | /api/patients | `list_patients` (api/routes/patient_routes.py:197) | List patients newest visit first (tenaga_kesehatan, admin) |
| GET | /api/patients/<pid> | `get_patient` (api/routes/patient_routes.py:220) | Return one record with per-role visibility |
| POST | /api/patients | `create_patient` (api/routes/patient_routes.py:243) | Create SOAP record with B03 range guard |
| PUT | /api/patients/<pid> | `update_patient` (api/routes/patient_routes.py:289) | Partial deep-merge update |
| DELETE | /api/patients/<pid> | `delete_patient` (api/routes/patient_routes.py:325) | Delete patient (admin only) |

Uses a module-level `threading.Lock` at api/routes/patient_routes.py:29 to serialise read-modify-write blocks.

#### drug_routes.py (blueprint `drug_routes`)

api/routes/drug_routes.py:16 Blueprint declared.

| Method | Path | View | Purpose |
|---|---|---|---|
| GET | /api/drugs | `list_drugs` (api/routes/drug_routes.py:30) | List catalog, optional `?category=` filter |
| GET | /api/drugs/search | `search_drugs` (api/routes/drug_routes.py:51) | Full-text search via anggota4.pencarian_obat |
| GET | /api/drugs/<nama_obat> | `get_drug` (api/routes/drug_routes.py:74) | Per-drug safety profile |

#### safety_routes.py (blueprint `safety_routes`)

api/routes/safety_routes.py:18 Blueprint declared.

| Method | Path | View | Purpose |
|---|---|---|---|
| POST | /api/safety/check | `safety_check` (api/routes/safety_routes.py:25) | Aggregate per-drug verdicts plus optional patient context |

Role-aware patient-context attachment: masyarakat role is silently denied (api/routes/safety_routes.py:72).

#### visualization_routes.py (blueprint `visualization_routes`)

api/routes/visualization_routes.py:16 Blueprint declared. anggota3 BacaData.py SyntaxError forces inline implementation (api/routes/visualization_routes.py:5).

| Method | Path | View | Purpose |
|---|---|---|---|
| GET | /api/visualizations/kunjungan-trend | `kunjungan_trend` (api/routes/visualization_routes.py:55) | 12-month visit trend |
| GET | /api/visualizations/keluhan-distribution | `keluhan_distribution` (api/routes/visualization_routes.py:77) | Patient distribution per kategori |
| GET | /api/visualizations/top-efek-samping | `top_efek_samping` (api/routes/visualization_routes.py:98) | Top 10 side effects across drug DB |
| GET | /api/visualizations/heatmap-efek | `heatmap_efek` (api/routes/visualization_routes.py:128) | Drug x effect matrix |

#### pdf_routes.py (blueprint `pdf_routes`)

api/routes/pdf_routes.py:32 Blueprint declared.

| Method | Path | View | Purpose |
|---|---|---|---|
| POST | /api/pdf/generate-rekam-medis | `generate_rekam_medis` (api/routes/pdf_routes.py:174) | Single-patient SOAP PDF |
| POST | /api/pdf/generate-laporan-bulanan | `generate_laporan_bulanan` (api/routes/pdf_routes.py:219) | Monthly recap PDF (admin only) |
| POST | /api/pdf/generate-efek-samping | `generate_efek_samping` (api/routes/pdf_routes.py:264) | Top adverse events report via fpdf2 |
| POST | /api/pdf/generate-inventaris | `generate_inventaris` (api/routes/pdf_routes.py:411) | Inventory report via fpdf2 |

#### admin_routes.py (blueprint `admin_routes`)

api/routes/admin_routes.py:21 Blueprint declared.

| Method | Path | View | Purpose |
|---|---|---|---|
| POST | /api/admin/scrape | `trigger_scrape` (api/routes/admin_routes.py:30) | Mocked 3-second scrape trigger |
| GET | /api/admin/users | `list_users` (api/routes/admin_routes.py:57) | List users with password fields stripped |
| POST | /api/admin/users | `create_user` (api/routes/admin_routes.py:71) | Create user with bcrypt hash |
| DELETE | /api/admin/users/<username> | `delete_user` (api/routes/admin_routes.py:122) | Delete user, refuse to remove last admin |
| GET | /api/admin/system-stats | `system_stats` (api/routes/admin_routes.py:150) | Live KPIs for admin dashboard |

### 1.8 PORT determination and desktop binding considerations

Today `PORT` is read once at api/config.py:43 from the `PORT` env var, defaulting to 8080. The Flask host is hardcoded to `0.0.0.0` at api/app.py:93. For a desktop dynamic-port binding the relevant changes are:

1. Replace the `app.run(...)` call at api/app.py:93 with a launcher that binds to `127.0.0.1` with port `0` (so the OS picks a free ephemeral port) and prints the resolved port to stdout, then the Electron parent process can capture it.
2. Alternatively keep the env-var pattern and let the parent process pass a known-free port via `MEDWATCH_PORT` env (avoid clashing with the existing Cloud Run `PORT` convention).
3. Either way, switch host from `0.0.0.0` to `127.0.0.1` for a desktop install so the bundled Flask is not exposed on the LAN.
4. CORS allowlist at api/config.py:28 needs the additional `app://` and `file://` protocol entries for Electron, or be replaced by a same-origin model where the static export and Flask serve from the same loopback address.

### 1.9 requirements.txt classification

api/requirements.txt:1 to api/requirements.txt:11 (11 packages):

| Package | Pin | Classification | Reason |
|---|---|---|---|
| Flask==3.1.3 | api/requirements.txt:1 | runtime-needed | Core HTTP server |
| Flask-Cors==6.0.0 | api/requirements.txt:2 | runtime-needed | CORS handling, needed because Electron may use a different origin |
| PyJWT==2.12.0 | api/requirements.txt:3 | runtime-needed | Token issuance and verification |
| bcrypt==4.2.1 | api/requirements.txt:4 | runtime-needed | Password hashing for offline auth |
| google-cloud-storage==2.18.2 | api/requirements.txt:5 | cloud-only, exclude from desktop | Only imported lazily inside `api/storage._gcs()` (api/storage.py:36) when `USE_CLOUD_STORAGE=true`. Desktop bundle should pin `USE_CLOUD_STORAGE=false` and either omit this dependency entirely or exclude it from the PyInstaller spec via `--exclude-module google.cloud.storage` to save approx 30 MB |
| gunicorn==23.0.0 | api/requirements.txt:6 | cloud-only, exclude from desktop | Cloud Run WSGI; Electron uses `app.run(...)` |
| requests==2.33.0 | api/requirements.txt:7 | runtime-needed | Used by anggota1/openfda/fetch.py; can be excluded from runtime once scrape has produced bundled SQLite, kept for safety |
| beautifulsoup4==4.12.3 | api/requirements.txt:8 | unclear | Required by anggota1.py for the drugs.com scraping path that is no longer used; PyInstaller will still pick it up if any anggota1 file imports it. UNVERIFIED whether dynamic bootstrap actually pulls it in at runtime |
| matplotlib==3.9.2 | api/requirements.txt:9 | unclear | anggota3 BacaData.py fails to import; visualization_routes.py:13 imports nothing from matplotlib directly. Likely safe to drop from desktop if anggota3 is fully avoided, but UNVERIFIED until bootstrap.get_module of anggota3 is tested |
| numpy==1.26.4 | api/requirements.txt:10 | unclear | Pulled in transitively by matplotlib. If matplotlib is dropped, numpy also drops. UNVERIFIED |
| fpdf2==2.8.1 | api/requirements.txt:11 | runtime-needed | Used directly at api/routes/pdf_routes.py:22 for efek-samping and inventaris PDFs |

Note: `flask-cors` exposes itself as `flask_cors`. The desktop spec needs to include it explicitly via hidden imports because PyInstaller does not always detect blueprint-discovered imports.

---

## 2. Frontend Next.js audit

### 2.1 Versions and config

- next.config.ts is at /Users/ghaisan/Documents/FrontendMedWatch/next.config.ts:1.
- Currently sets `transpilePackages: ["react-force-graph-2d", "force-graph"]` (next.config.ts:4) and `images.unoptimized: true` (next.config.ts:5). The `images.unoptimized: true` is already aligned with static export requirements.
- No `output: "export"` field is currently set, so today's deployment is server-rendered (Vercel build).

- package.json at /Users/ghaisan/Documents/FrontendMedWatch/package.json:1.
- Next.js version: `next: 16.2.1` (package.json:26).
- React: `react: 19.2.4`, `react-dom: 19.2.4` (package.json:28 to package.json:29).
- TypeScript: `^5` (package.json:55).
- Tailwind: `tailwindcss: ^4`, `@tailwindcss/postcss: ^4` (package.json:54 and package.json:42).
- shadcn: `^4.1.1` (package.json:33).
- App router (no `pages/` directory).

### 2.2 Server feature surface

Searched src/ with grep for `'use server'`, `cookies()`, `headers()`, `next/server`, `export const dynamic`, `export const revalidate`, `unstable_`, `generateStaticParams`.

Hits (verbatim file:line):
- src/app/api/[...slug]/route.ts:19  `import { NextRequest, NextResponse } from "next/server";`
- src/app/api/[...slug]/route.ts:62  `const cookieStore = await cookies();`
- src/app/safety-checker/page.tsx:21  `export const dynamic = "force-dynamic";`
- src/app/drug-comparison/page.tsx:19  `export const dynamic = "force-dynamic";`
- src/app/login/page.tsx:19  `export const dynamic = "force-dynamic";`
- src/proxy.ts:1 to src/proxy.ts:139  Edge proxy (renamed from `middleware.ts`) that imports `next/server` and uses `req.cookies`.

No `'use server'` directives, no `unstable_*`, no `generateStaticParams`, no `export const revalidate` were found in `src/`.

### 2.3 next/image audit

Only hit: src/proxy.ts:137 `"/((?!api|_next/static|_next/image|favicon.ico|.*\\.(?:png|jpg|jpeg|gif|svg|webp|ico)$).*)"`. This is the matcher regex, not a usage of `next/image`. UNVERIFIED whether any component below `components/` uses `next/image` (Grep did not hit). `images.unoptimized: true` is already set in next.config.ts:5, so this is safe regardless.

### 2.4 Page-by-page export-readiness table

Columns: path | uses_server_features (Y/N) | which_features | static_export_ready (Y/N) | notes

| Path | Server | Which | Export-ready | Notes |
|---|---|---|---|---|
| src/app/layout.tsx | N | none | Y | Root layout. UNVERIFIED beyond the head/body wrap because file content not fully read; no server imports in first 25 lines of any page. |
| src/app/page.tsx | N (uses redirect) | `redirect` from `next/navigation` | partial | src/app/page.tsx:6 imports `redirect`; redirect to `/dashboard` resolves at request time. For static export this needs to become a client-side replace or move into `proxy.ts`. |
| src/app/visualization/page.tsx | N | "use client" only | Y | Pure client component, all data fetched on mount via `@/lib/api`. |
| src/app/patients/page.tsx | N | "use client" only | Y | Client-side patient roster fetch on mount. |
| src/app/drug-search/page.tsx | N | "use client" only | Y | Client list fetch. |
| src/app/dashboard/page.tsx | N | "use client" only | Y | Client KPI dashboard. |
| src/app/export-pdf/page.tsx | N | "use client" only | Y | Client form, downloads via `downloadBlob`. |
| src/app/safety-checker/page.tsx | Y | `export const dynamic = "force-dynamic"` (line 21), uses `useSearchParams` | Needs change | Remove the `dynamic` export and wrap `useSearchParams` in `<Suspense>` (already wrapped per file header). After removing the dynamic flag, this page is static-export safe because data fetch is client-side. |
| src/app/heatmap/page.tsx | N | "use client" only | Y | Client heatmap render. |
| src/app/drug-comparison/page.tsx | Y | `export const dynamic = "force-dynamic"` (line 19), uses `useSearchParams` | Needs change | Same recipe as safety-checker: drop the dynamic flag, keep Suspense boundary. |
| src/app/export/page.tsx | N | "use client" only | Y | Client export form. |
| src/app/login/page.tsx | Y | `export const dynamic = "force-dynamic"` (line 19), uses `useSearchParams` | Needs change | Drop the dynamic flag; the cookie write happens through the API route, which the desktop variant will replace with a same-origin call to Flask. |
| src/app/patients/new/page.tsx | N | "use client" only | Y | Client form. |
| src/app/patients/[id]/page.tsx | N | "use client" only, uses `useParams` | Y, but requires `generateStaticParams` strategy | Dynamic segment. For static export, must generate stub params for every possible id (impossible) OR use `dynamicParams: true` only available in non-static. Workable approach: ship as a fully client-side router page where `[id]` is read at runtime. UNVERIFIED whether Next 16 honours this without `generateStaticParams`; likely needs `dynamicParams = true` + `revalidate = 0` or migration to a non-dynamic route shape with the id passed via search params. |
| src/app/admin/scraper/page.tsx | N | "use client" only | Y | Client scraper panel. |
| src/app/admin/dashboard/page.tsx | N | "use client" only | Y | Client KPIs. |
| src/app/admin/users/page.tsx | N | "use client" only | Y | Client roster fetch. |
| src/app/dashboard/aktivitas/page.tsx | N | "use client" only | Y | Client feed page. |
| src/app/pasien/profile/page.tsx | N | "use client" only | Y | Client profile page. |
| src/app/_archived/* | N | varies | Skip | Underscore prefix excludes them from routing. |
| src/app/api/[...slug]/route.ts | Y | full server route, uses `cookies()`, `next/server` | N | Must be removed or replaced for static export. In the desktop variant, the catch-all proxy is unnecessary because the static build can call the bundled Flask directly on localhost:<port>. Strategy: delete `src/app/api/` in the desktop build, replace `src/lib/api` base URL with `http://127.0.0.1:<port>`. |
| src/proxy.ts | Y | edge runtime, uses `next/server`, decodes JWT cookie | N | Static export does not run edge middleware. The desktop variant must move role-gating into client-side React (read JWT from localStorage or `document.cookie`, then push to `/login` if absent). |

### 2.5 Net static-export-readiness summary

- 4 server-rendered surfaces block today's `next build` from producing a clean static export: `src/app/api/[...slug]/route.ts`, `src/proxy.ts`, the three `export const dynamic = "force-dynamic"` pages (login, safety-checker, drug-comparison), and the root `src/app/page.tsx` that calls `redirect()`.
- 1 dynamic route `[id]` will need a strategy (likely a client-only shell that reads the id at runtime).
- Wave 3 needs to introduce a build mode flag (env var, e.g. `NEXT_PUBLIC_DESKTOP=true`) that:
  - Sets `output: "export"` in next.config.ts.
  - Removes the three `dynamic = "force-dynamic"` exports.
  - Skips bundling `src/app/api/`.
  - Replaces `src/proxy.ts` middleware with a client-side guard.
  - Rewrites `src/app/page.tsx` to render a client-side router push.
  - Rewires `src/lib/api` (UNVERIFIED, not read in this scout pass) to point at `http://127.0.0.1:<port>` with the port injected by Electron at runtime via `window.MEDWATCH_PORT` or a generated `config.json`.

---

## 3. openFDA endpoint health

All five probes were executed with curl on 2026-05-25 using `OPENFDA_API_KEY` from env. The key value was never printed; the resolved URL was never logged. The commands used were of the shape:

```
curl -s "https://api.fda.gov/drug/<ep>?<params>&api_key=$OPENFDA_API_KEY" | python3 -c '...'
```

### 3.1 Result counts (meta.results.total)

| Endpoint | Probe | total |
|---|---|---|
| /drug/label.json | limit=1 | 258334 |
| /drug/ndc.json | limit=1 | 135206 |
| /drug/ndc.json | search=finished:true AND product_type:"HUMAN PRESCRIPTION DRUG", limit=1 | 55666 |
| /drug/event.json | limit=1 | 20328575 |
| /drug/enforcement.json | limit=1 | 17661 |

The Wave 4 SQLite bundle targets the 55666 HUMAN PRESCRIPTION DRUG NDC records. With the authenticated rate limit of 240 req/min (see 3.2) and a sustainable batch size of 1000 records per call via `limit=1000`, the full pull takes approximately 56 calls (about 15 seconds at full throttle). UNVERIFIED whether the openFDA daily quota for the authenticated key (120 000 req/day per the .env.example:2 comment) holds; not exercised in this recon.

### 3.2 Rate-limit headers and paging support

`curl -s -D - -o /dev/null` against `https://api.fda.gov/drug/ndc.json?limit=1&api_key=$OPENFDA_API_KEY` returned:

```
content-type: application/json; charset=utf-8
link: <https://api.fda.gov/drug/ndc.json?limit=1&skip=0&search_after=0%3D--KtUp4BM7UYVJyIK04t>; rel="next"
x-ratelimit-limit: 240
x-ratelimit-remaining: 234
```

Findings:
- Rate limit is 240 requests per minute (per IP, with key).
- After 6 calls in this recon session, 234 remaining confirms the limit ticks down per call.
- `Link: rel="next"` returns a `search_after` cursor, which means the openFDA `search_after` pagination strategy is available even without specifying it explicitly. The cursor is opaque (`search_after=0%3D--KtUp4BM7UYVJyIK04t`) and contains no PII.
- The same `Link` header was present for the prescription-drug filtered query (`search_after=0%3D--OtUp4BM7UYVJyId6Oi`).

Implication for Wave 4: paging via the `Link: rel="next"` header is the correct strategy. Continue requesting until the response carries no `Link` next.

### 3.3 Sample NDC schema (for SQLite design)

Top-level keys of `/drug/ndc.json` results[0] (with `search=finished:true+AND+product_type:"HUMAN+PRESCRIPTION+DRUG"`):

```
product_ndc, generic_name, labeler_name, brand_name, active_ingredients,
finished, packaging, listing_expiration_date, openfda, marketing_category,
dosage_form, spl_id, product_type, route, marketing_start_date, product_id,
application_number, brand_name_base, pharm_class
```

This is the candidate set for the SQLite column layout. Recommend a flat table `drugs_ndc(product_ndc PK, brand_name, generic_name, labeler_name, dosage_form, route, marketing_start_date, application_number, pharm_class TEXT[json], active_ingredients TEXT[json], packaging TEXT[json])` plus a virtual FTS5 mirror for autocomplete.

---

## 4. Prior anggota1 scraper inventory

### 4.1 anggota1/openfda/fetch.py

Path: anggota1/openfda/fetch.py (21259 bytes).

- Module docstring at anggota1/openfda/fetch.py:1 confirms it is the "openFDA acquisition script" replacing the blocked drugs.com path.
- Constants block at anggota1/openfda/fetch.py:48 to anggota1/openfda/fetch.py:102 defines the FAERS endpoint (`https://api.fda.gov/drug/event.json`), the enforcement endpoint (`https://api.fda.gov/drug/enforcement.json`), polite-delay `POLITE_DELAY_S = 0.25`, page size 1000 for recalls, and the bundled `DEFAULT_DRUGS` list of about 75 INNs.
- Category mapping at anggota1/openfda/fetch.py:109 to anggota1/openfda/fetch.py:133 buckets each drug into a coarse therapeutic category. Useful for Wave 4 SQLite indexing.
- Request shape: `fetch_json(url, params, *, timeout, max_retries)` at anggota1/openfda/fetch.py:164 to anggota1/openfda/fetch.py:223 calls `requests.get(url, params=params, timeout=timeout)`, treats 404 as empty, retries on 429 and 5xx with `_backoff_seconds(attempt)` at anggota1/openfda/fetch.py:226 (exponential, jitter, capped at 30s, max 5 retries).
- Logging redaction: `_redact_params(params)` at anggota1/openfda/fetch.py:156 replaces `api_key` value with `<redacted>`. Logged URLs never carry the key. Reusable verbatim for Wave 4.
- Source URL builder `_build_source_url` at anggota1/openfda/fetch.py:445 also uses the redacted params dict.
- Output: writes JSON via `write_json(path, records)` at anggota1/openfda/fetch.py:479 (no incremental streaming; full list serialised at the end).
- Pagination strategy: enforcement endpoint uses `limit=1000` + `skip=page*1000` with `sort=recall_initiation_date:desc` in `fetch_drug_recalls(api_key, *, max_pages=26, page_size=1000)` at anggota1/openfda/fetch.py:392. Does not use `search_after`; this is fine for under-26000 records but Wave 4 should switch to `search_after` for the 55666-record NDC pull to avoid the documented openFDA 26000-record skip limit (UNVERIFIED but openFDA docs are explicit on this).
- Adverse-event aggregation strategy: three calls per drug (top reactions, total report count, serious fraction, death fraction) combined at anggota1/openfda/fetch.py:257 to anggota1/openfda/fetch.py:349. Output schema is `{drug_name, category, side_effects, severity_level, warnings, source_url}`.

Reusable concepts for Wave 4 (no code copy, just patterns):
1. The `fetch_json` retry-with-backoff loop and the `_redact_params` redactor are directly portable.
2. The polite 250 ms delay between requests is well below the 240 rpm limit (would need 4 calls/sec to hit the cap) and is a good default for the SQLite bulk pull.
3. The category-mapping dict is a reasonable starter for Wave 4's secondary categorisation of NDC records by therapeutic class.

### 4.2 anggota1/scraper.log

- File timestamp: May 11 09:06:02 2026 UTC (mtime).
- Content: 2674 bytes documenting an earlier failed drugs.com scrape (HTTP 403 on every drug query) that ran on the legacy `anggota1.py` path, not on the new openFDA `fetch.py`. The log ends with `selesai. safety=0 baris, recalls=0 baris`, meaning the captured run wrote zero records.
- This means the canonical `anggota1/data/drug_safety_data.json` was produced by a later `anggota1/openfda/fetch.py` run not captured in this log (file mtime is May 18 14:13 UTC, a week after the log).

### 4.3 anggota1/data/drug_safety_data.json shape

- File: 78655 bytes, last modified May 18 14:13:26 UTC 2026.
- Loaded count: 74 records (confirmed by `len(json.load(...))`).
- Each record carries keys: `drug_name, category, side_effects, severity_level, warnings, source_url`.
- `side_effects` is a list of up to 25 MedDRA preferred terms in Title Case (sample: paracetamol record carries 25 terms beginning with `Toxicity To Various Agents`, `Vomiting`, `Nausea`).
- `severity_level` is one of `ringan`, `sedang`, `serius` (per `_severity_from_event_aggregate` at anggota1/openfda/fetch.py:236).
- `warnings` is a single Indonesian-language paragraph synthesised from the FAERS aggregate.
- `source_url` is the redacted FAERS URL for traceability (key replaced by `<redacted>`).
- All 74 `source_url` strings are unique. No duplicates.

For Wave 4 the table schema for adverse-event data should include `drug_name (UNIQUE), category, side_effects_json TEXT, severity_level, warnings, source_url`.

### 4.4 anggota1/data/drug_recalls.json

- File: 2561016 bytes, last modified May 18 14:13:41 UTC 2026. About 2.4 MB.
- Not read line-by-line in this recon (large file); inferred schema from anggota1/openfda/fetch.py:424 to anggota1/openfda/fetch.py:431: `{product_name, reason, recall_date, severity_class, company}`.

---

## 5. Tooling reality check

Output of probes:

| Tool | Result | Implication |
|---|---|---|
| `which pyinstaller` | not found | Wave 1 must `pip install pyinstaller` into the backend venv. PyInstaller stable releases support Python 3.13. Python 3.14 is NOT officially supported as of PyInstaller 6.10. UNVERIFIED whether the unreleased PyInstaller `develop` branch supports 3.14, but Wave 2 must either pin to Python 3.13 via pyenv or use the cx_Freeze fallback. |
| `which wine` | not found | Cross-compiling a Windows `.exe` from macOS is blocked. Wave 5 must either: (a) provision a Windows VM/runner, (b) use a GitHub Actions Windows runner, (c) document that the final installer will be produced from a Windows machine. PyInstaller does not cross-compile per its docs. |
| `which electron-builder` | not found | Expected; Wave 1 installs it via npm. |
| `python3 -c "import sys; print(sys.version)"` | `3.14.5 (main, May 10 2026, 10:21:34) [Clang 21.0.0 (clang-2100.0.123.102)]` | Python 3.14 on this dev host conflicts with the PyInstaller 6.10 stable Python support matrix (3.8 to 3.13). The CLAUDE.md target was Python 3.11; this host has 3.14. Wave 1 must install a 3.11 or 3.13 interpreter (recommend pyenv) so the PyInstaller bundle matches the project pin. |
| `node --version` | `v25.6.0` | Recent. electron-builder 24.x supports Node 16+. Fine. |
| `npm --version` | `11.9.0` | Fine. |

### 5.1 Existing PyInstaller artifacts

- /Users/ghaisan/Documents/MedWatchIntegration/medWatch/ProductionGrade-ImplementationPlan/build/medwatch.spec exists.
- /Users/ghaisan/Documents/MedWatchIntegration/medWatch/ArtifactReadySubmit/09-ProductionGrade-Plan/medwatch.spec exists.

These were not read in this scout pass and are out of the integration mission scope as documented in CLAUDE.md (they were produced for an earlier presentation track). Wave 2 should treat them as inspiration only and author a fresh `medwatch_desktop.spec`.

### 5.2 Procfile and Dockerfile

- /Users/ghaisan/Documents/MedWatchIntegration/medWatch/Procfile and /Users/ghaisan/Documents/MedWatchIntegration/medWatch/Dockerfile exist for the Cloud Run track.
- /Users/ghaisan/Documents/MedWatchIntegration/medWatch/api/Dockerfile exists with the canonical Cloud Run build.
- Desktop bundle does not interact with these.

---

## 6. Open items and recommendations for Wave 1

1. PyInstaller Python version: Wave 1 must standardise on Python 3.11 (CLAUDE.md target) or 3.13 (PyInstaller stable). The dev host runs Python 3.14, which neither supports.
2. CORS allowlist hardcoded in api/config.py:28 must accept either `http://127.0.0.1:*` or move to env-driven for the desktop port mapping to work.
3. The host binding at api/app.py:93 must change from `0.0.0.0` to `127.0.0.1` for desktop installs.
4. The three pages with `export const dynamic = "force-dynamic"` are the primary blockers for `next build` with `output: "export"`.
5. The catch-all proxy at src/app/api/[...slug]/route.ts:1 and the edge middleware at src/proxy.ts:1 are not compatible with static export and must be replaced with client-side equivalents in the desktop variant.
6. The 55666 HUMAN PRESCRIPTION DRUG NDC corpus is well within feasible scrape range (about 56 calls at limit=1000, rate-limit comfortable at 240 rpm).
7. The bundled `anggota1/data/drug_safety_data.json` (74 records, FAERS-derived) is independent from the planned NDC SQLite bundle. Wave 4 may choose to either fold the safety data into the same SQLite or keep it as a separate JSON shipped alongside.
8. Cross-compile blocker: Wave 5 final installer .exe production must happen on a Windows machine. Document this as a Phase H gate.

---

## 7. Recon commands run (for evidence)

The following commands were executed during this recon. None of them logged or printed the value of `OPENFDA_API_KEY`.

- `ls -la /Users/ghaisan/Documents/MedWatchIntegration/medWatch/`
- `ls -la /Users/ghaisan/Documents/MedWatchIntegration/medWatch/api/`
- `ls -la /Users/ghaisan/Documents/MedWatchIntegration/medWatch/api/routes/`
- `ls -la /Users/ghaisan/Documents/MedWatchIntegration/medWatch/anggota1/`
- `ls -la /Users/ghaisan/Documents/MedWatchIntegration/medWatch/.mission/`
- `find /Users/ghaisan/Documents/FrontendMedWatch -maxdepth 2 -name "next.config*" -o -name "package.json"`
- `find /Users/ghaisan/Documents/FrontendMedWatch/src/app -type f \( -name page.tsx -o -name layout.tsx -o -name route.ts -o -name route.tsx \)`
- `find /Users/ghaisan/Documents/FrontendMedWatch/src/app -type d`
- `grep -rEn "'use server'|cookies\(\)|headers\(\)|next/server|dynamic|revalidate|unstable_|generateStaticParams" src/app`
- `grep -rEn "next/image" src/`
- `which pyinstaller wine electron-builder`
- `python3 -c "import sys; print(sys.version)"`
- `node --version`, `npm --version`
- `curl -s "https://api.fda.gov/drug/label.json?limit=1&api_key=$OPENFDA_API_KEY" | python3 -c '...'`
- `curl -s "https://api.fda.gov/drug/ndc.json?limit=1&api_key=$OPENFDA_API_KEY" | python3 -c '...'`
- `curl -s "https://api.fda.gov/drug/ndc.json?search=finished:true+AND+product_type:%22HUMAN+PRESCRIPTION+DRUG%22&limit=1&api_key=$OPENFDA_API_KEY" | python3 -c '...'`
- `curl -s "https://api.fda.gov/drug/event.json?limit=1&api_key=$OPENFDA_API_KEY" | python3 -c '...'`
- `curl -s "https://api.fda.gov/drug/enforcement.json?limit=1&api_key=$OPENFDA_API_KEY" | python3 -c '...'`
- `curl -s -D - -o /dev/null "https://api.fda.gov/drug/ndc.json?limit=1&api_key=$OPENFDA_API_KEY"` (rate-limit headers)
- `python3 -c "import json; d=json.load(open('.../drug_safety_data.json')); print('records:',len(d))"`
- `tail -20 anggota1/scraper.log`
- `stat -f '%SmZ %z %N' anggota1/data/drug_safety_data.json anggota1/data/drug_recalls.json`

End of Wave 0 scout findings.
