# MedWatch API (`api/`)

Flask integration layer wrapping modul anggota1 sampai anggota5 menjadi REST endpoints. Deployed on GCP Cloud Run, asia-southeast1, behind a Vercel API proxy.

## Tech stack

- Python 3.11 (Cloud Run runtime via root `Dockerfile`)
- Flask 3.0 + Flask-Cors
- PyJWT 2.10 for stateless JWT (HS256, 12h expiry)
- bcrypt 4.2 for password hashing (cost 12)
- gunicorn 23 for production WSGI (2 workers, 4 threads)
- google-cloud-storage 2.18 for users.json + patients.json persistence
- fpdf2 2.8 (re-uses anggota5/export_pdf)

## Quick start (local dev)

```bash
cd medWatch
pip install -r api/requirements.txt
JWT_SECRET=dev-only python -m flask --app api.app run --port 8080
```

Server starts on http://localhost:8080. Visit `/` for the API documentation page.

## Quick start (smoke test against deployed Cloud Run)

```bash
BASE_URL=https://medwatch-api-517694123086.asia-southeast1.run.app \
  python3 api/tests/smoke_test.py
```

## Endpoint reference

### Auth

| Method | Path | Role | Body | Response |
|---|---|---|---|---|
| POST | `/api/auth/login` | public | `{username, password}` | `{token, user: {username, role, name}}` |
| GET | `/api/auth/me` | any | - | `{username, role, name}` |
| POST | `/api/auth/logout` | public | - | `{status}` |

### Patients (SOAP shape per anggota2 canonical schema)

| Method | Path | Role | Notes |
|---|---|---|---|
| GET | `/api/patients` | tenaga_kesehatan, admin | List summary |
| GET | `/api/patients/<id>` | any (own only for masyarakat) | Full SOAP record |
| POST | `/api/patients` | tenaga_kesehatan, admin | Auto-assign id `P001`, `P002`... via anggota2.pasien_helper.generate_id |
| PUT | `/api/patients/<id>` | tenaga_kesehatan, admin | Deep-merge update |
| DELETE | `/api/patients/<id>` | admin | - |

### Drugs (wraps anggota4)

| Method | Path | Role | Notes |
|---|---|---|---|
| GET | `/api/drugs` | public | All drugs, optional `?category=` filter |
| GET | `/api/drugs/search?q=` | public | Search by name/alias/indication |
| GET | `/api/drugs/<nama>` | public | Full profile + safety analysis |

### Safety check (wraps anggota4.safety_checker)

| Method | Path | Role | Body | Response |
|---|---|---|---|---|
| POST | `/api/safety/check` | any auth | `{drugs: [...], pasien_id?}` | `{drugs[], interactions[], severity_score, severity_level (low/medium/high), warnings[], obat_tidak_ditemukan[], pasien_context}` |

Per-drug `skor_risiko` (0-100) and `label_risiko` (rendah/sedang/tinggi) come from anggota4 directly. Aggregate `severity_score` is `max(skor_risiko)` across drugs; `severity_level` is the worst label.

### Visualizations (Recharts JSON, NOT matplotlib PNG)

`anggota3/BacaData.py` has a known SyntaxError (line 204), so this module implements equivalent data extraction inline from `api/data/patients.json` + `anggota4/data/drug_database.json`.

| Method | Path | Role | Returns |
|---|---|---|---|
| GET | `/api/visualizations/kunjungan-trend` | tenaga_kesehatan, admin | `[{month, count}, ...]` |
| GET | `/api/visualizations/keluhan-distribution` | tenaga_kesehatan, admin | `[{kategori, count}, ...]` |
| GET | `/api/visualizations/top-efek-samping` | any auth | Top 10 effects across drug catalog |
| GET | `/api/visualizations/heatmap-efek` | any auth | `{drugs[], effects[], values[][]}` |

### PDF (wraps anggota5/export_pdf)

| Method | Path | Role | Body | Response |
|---|---|---|---|---|
| POST | `/api/pdf/generate-rekam-medis` | tenaga_kesehatan, admin | `{pasien_id}` | application/pdf binary |
| POST | `/api/pdf/generate-laporan-bulanan` | admin | `{month: "YYYY-MM"}` | application/pdf binary |

Schema translation from canonical SOAP to anggota5's nested `{identitas, anamnesis, pemeriksaan, diagnosis_tindakan}` happens inline in `pdf_routes._to_anggota5_format`.

### Admin

| Method | Path | Role | Body | Notes |
|---|---|---|---|---|
| POST | `/api/admin/scrape` | admin | - | Mocked (3-second simulated delay) |
| GET | `/api/admin/users` | admin | - | List users (no password fields) |
| POST | `/api/admin/users` | admin | `{username?, password, role, name, phone}` | Auto-generate username from name+phone if absent |
| DELETE | `/api/admin/users/<username>` | admin | - | Refuses to delete last admin |
| GET | `/api/admin/system-stats` | admin | - | Counts + last_scrape + by_role |

## Demo credentials

Seed `users.json` ships with `password_plain` fields. On first server read, `storage.load_users()` bcrypt-hashes them and rewrites the file (or GCS object). Plaintext is never persisted long-term.

| Username | Password | Role |
|---|---|---|
| `bidan_siti` | `siti2026` | tenaga_kesehatan |
| `bidan_putri` | `putri2026` | tenaga_kesehatan |
| `umum_budi` | `budi2026` | masyarakat |
| `umum_dewi` | `dewi2026` | masyarakat |
| `admin_ghaisan` | `admin2026` | admin |
| `admin_sistem` | `system2026` | admin |

## Environment variables

| Name | Default | Purpose |
|---|---|---|
| `JWT_SECRET` | `dev-only-do-not-use-in-prod` | HS256 signing key (Cloud Run injects from Secret Manager) |
| `USE_CLOUD_STORAGE` | `false` | Toggle GCS persistence vs local JSON |
| `GCP_PROJECT_ID` | `medwatch-polban-2026` | - |
| `GCS_BUCKET` | `medwatch-polban-2026-state` | - |
| `PORT` | `8080` | gunicorn port |
| `FLASK_DEBUG` | `false` | NEVER true in production |

## Architecture

See `../docs/diagrams/` for the full set of 18 diagrams (drawio source + PNG):

- **System context, container, component:** `01-c4-context`, `02-c4-container`, `03-c4-component-api`
- **UML:** `04-use-case`, `05-class-diagram`, `06-sequence-auth`, `07-sequence-patient-create`, `08-sequence-safety-check`, `09-activity-patient-flow`, `10-state-auth-session`
- **Data:** `11-er-schema`
- **Infra:** `12-deployment`, `13-network-topology`
- **Per-anggota structure:** `14-structure-chart-anggota1` through `18-structure-chart-anggota5`

## Security model

- JWT lives in **httpOnly Secure SameSite=Lax cookies** set by the Vercel proxy. Browser-side JavaScript never touches the token (XSS-resistant).
- Vercel API proxy at `/app/api/[...slug]/route.ts` forwards all `/api/*` traffic to Cloud Run with `Authorization: Bearer <token>` injected from cookie.
- bcrypt cost 12.
- CORS allowlist: only Vercel deployment URL + localhost dev ports.
- Cloud Run service account has minimal IAM: `objectAdmin` on the state bucket only, `secretAccessor` on `medwatch-jwt-secret` only.
- Cloud Storage bucket is private (no `allUsers` binding).
- See `../docs/SECURITY_AUDIT.md` for the full OWASP Top 10 review.

## Deployment commands

```bash
# Initial setup (one-time)
gcloud projects create medwatch-polban-2026 --name="MedWatch POLBAN 2026"
gcloud beta billing projects link medwatch-polban-2026 --billing-account=$BILLING_ACCT
gcloud config set project medwatch-polban-2026
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com storage-component.googleapis.com secretmanager.googleapis.com iam.googleapis.com
gsutil mb -l asia-southeast1 -p medwatch-polban-2026 gs://medwatch-polban-2026-state
gsutil versioning set on gs://medwatch-polban-2026-state
gsutil cp api/data/users.json gs://medwatch-polban-2026-state/users.json
echo '[]' | gsutil cp - gs://medwatch-polban-2026-state/patients.json
openssl rand -base64 64 | gcloud secrets create medwatch-jwt-secret --data-file=- --replication-policy=automatic

# Grant service account access
PROJECT_NUMBER=$(gcloud projects describe medwatch-polban-2026 --format='value(projectNumber)')
SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
gcloud secrets add-iam-policy-binding medwatch-jwt-secret --member="serviceAccount:${SA}" --role="roles/secretmanager.secretAccessor"
gsutil iam ch "serviceAccount:${SA}:objectAdmin" gs://medwatch-polban-2026-state

# Deploy (re-run for updates)
gcloud run deploy medwatch-api \
  --source . --clear-base-image \
  --region asia-southeast1 --platform managed --allow-unauthenticated \
  --memory 1Gi --cpu 1 --timeout 120 --port 8080 \
  --set-env-vars "USE_CLOUD_STORAGE=true,GCP_PROJECT_ID=medwatch-polban-2026,GCS_BUCKET=medwatch-polban-2026-state" \
  --set-secrets "JWT_SECRET=medwatch-jwt-secret:latest"
```

## Known limitations

- Scraper trigger is mocked (3-second simulated delay returning cached drug count). Real Selenium-style scraping in `anggota1` remains intact and runnable manually.
- Drug database has 12 entries (from `anggota4/data/drug_database.json`).
- No automated tests beyond `tests/smoke_test.py`.
- Cold start on Cloud Run: 2-3 seconds for first request after idle.
- JWT cannot be revoked server-side without a denylist (stateless trade-off mitigated by 12h expiry + httpOnly cookie).

## Authors and ownership

- `api/` layer authored by Ghaisan Khoirul Badruzaman as the integration deliverable.
- `anggota1`-`anggota5` modules belong to teammates Ghaisan, Bimo, Alia, Iqbal, Abhidal respectively (read-only from this layer's perspective).
- Abhidal-authorized one-time revision to `anggota5/{auth.py, data/users.json, tkesehatan_crud.py, main_anggota5.py}` is included in the `ghaisan-APIIntegration` branch and the same PR.
