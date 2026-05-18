# MedWatch Integration Guide

End-to-end developer guide for the integrated MedWatch system: backend Flask API on Cloud Run, frontend Next.js on Vercel, JWT auth, role-based access.

## Live URLs

- **Frontend (Vercel):** https://medwatch-frontend.vercel.app
- **Backend (Cloud Run):** https://medwatch-api-517694123086.asia-southeast1.run.app
- **API documentation:** https://medwatch-api-517694123086.asia-southeast1.run.app/

## Repositories

- **Backend:** https://github.com/Bisura16/medWatch (branch `ghaisan-APIIntegration`)
- **Frontend:** https://github.com/Finerium/FrontendMedwatch (branch `ghaisan-APIIntegration`)

## Demo credentials

| Role | Username | Password | Web access |
|---|---|---|---|
| Admin | `admin_ghaisan` | `admin2026` | All pages incl. `/admin/*` |
| Admin | `admin_sistem` | `system2026` | All pages incl. `/admin/*` |
| Tenaga Kesehatan | `bidan_siti` | `siti2026` | All clinical pages |
| Tenaga Kesehatan | `bidan_putri` | `putri2026` | All clinical pages |
| Masyarakat | `umum_budi` | `budi2026` | Profile + drug search + safety check |
| Masyarakat | `umum_dewi` | `dewi2026` | Profile + drug search + safety check |

## Architecture summary

The integration uses a Vercel API proxy pattern (security pattern B):

1. Browser only ever sees `https://medwatch-frontend.vercel.app`.
2. Browser-side JavaScript hits relative `/api/...` paths.
3. Vercel App Router catches `/api/[...slug]/route.ts` and forwards to Cloud Run with the JWT cookie attached as `Authorization: Bearer ...`.
4. Cloud Run runs Flask api/ which wraps modul anggota1-5 (read-only) and persists state in GCS bucket.

JWT lives in `httpOnly Secure SameSite=Lax` cookies (XSS-resistant). The backend Cloud Run URL is in `BACKEND_API_URL` Vercel env var, server-side only (no `NEXT_PUBLIC_` prefix), so it is never exposed to the browser.

See `diagrams/02-c4-container.png` and `diagrams/12-deployment.png` for visual reference.

## Run locally

### Backend

```bash
cd medWatch
pip install -r api/requirements.txt
JWT_SECRET=dev-only python -m flask --app api.app run --port 8080
```

Server at http://localhost:8080. Visit `/` for endpoint docs.

Smoke test:
```bash
BASE_URL=http://localhost:8080 python3 api/tests/smoke_test.py
```

### Frontend pointing to local backend

```bash
cd FrontendMedwatch
echo "BACKEND_API_URL=http://localhost:8080" > .env.local
npm install
npm run dev
```

Frontend at http://localhost:3000. Login with any demo credential.

## Deploy fresh copy

Recreate from scratch:

```bash
# 1. GCP project
gcloud projects create medwatch-polban-2026 --name="MedWatch POLBAN 2026"
gcloud beta billing projects link medwatch-polban-2026 --billing-account=$(gcloud beta billing accounts list --filter='open=true' --format='value(name)' | head -1)
gcloud config set project medwatch-polban-2026
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com storage-component.googleapis.com secretmanager.googleapis.com iam.googleapis.com

# 2. Storage + secret
gsutil mb -l asia-southeast1 gs://medwatch-polban-2026-state
gsutil versioning set on gs://medwatch-polban-2026-state
gsutil cp api/data/users.json gs://medwatch-polban-2026-state/users.json
echo '[]' | gsutil cp - gs://medwatch-polban-2026-state/patients.json
openssl rand -base64 64 | gcloud secrets create medwatch-jwt-secret --data-file=- --replication-policy=automatic

# 3. IAM
PROJECT_NUMBER=$(gcloud projects describe medwatch-polban-2026 --format='value(projectNumber)')
SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
gcloud secrets add-iam-policy-binding medwatch-jwt-secret --member="serviceAccount:${SA}" --role="roles/secretmanager.secretAccessor"
gsutil iam ch "serviceAccount:${SA}:objectAdmin" gs://medwatch-polban-2026-state

# 4. Deploy
cd medWatch
gcloud run deploy medwatch-api --source . --clear-base-image \
  --region asia-southeast1 --platform managed --allow-unauthenticated \
  --memory 1Gi --cpu 1 --timeout 120 --port 8080 \
  --set-env-vars "USE_CLOUD_STORAGE=true,GCP_PROJECT_ID=medwatch-polban-2026,GCS_BUCKET=medwatch-polban-2026-state" \
  --set-secrets "JWT_SECRET=medwatch-jwt-secret:latest"

# 5. Vercel
cd ../FrontendMedwatch
vercel link  # choose Finerium/medwatch-frontend
BACKEND_URL=$(gcloud run services describe medwatch-api --region asia-southeast1 --format='value(status.url)')
printf '%s' "$BACKEND_URL" | vercel env add BACKEND_API_URL production
vercel --prod
```

## Add a new endpoint

1. Add a route file in `medWatch/api/routes/<name>_routes.py`:
   ```python
   from flask import Blueprint
   from ..middleware import require_role
   from ..helpers import ok

   bp = Blueprint("name_routes", __name__)

   @bp.route("/api/something", methods=["GET"])
   @require_role("admin")
   def something():
       return ok({"hello": "world"})
   ```

2. Register in `medWatch/api/app.py`:
   ```python
   from api.routes import name_routes
   app.register_blueprint(name_routes.bp)
   ```

3. Smoke test:
   ```python
   def test_something():
       r = requests.get(f"{BASE}/api/something", headers=...)
       assert r.status_code == 200
   ```

4. Re-deploy:
   ```bash
   gcloud run deploy medwatch-api --source . --clear-base-image \
     --region asia-southeast1 --project medwatch-polban-2026
   ```

## Add a new user

```bash
TOKEN=$(curl -s -X POST $BACKEND_URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin_ghaisan","password":"admin2026"}' | jq -r .token)

curl -X POST $BACKEND_URL/api/admin/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Bidan Yuni", "phone":"081234567899", "role":"tenaga_kesehatan", "password":"yuni2026"}'
```

Or via the frontend at `/admin/users`.

## Key files

| Concern | Location |
|---|---|
| Backend entry | `medWatch/api/app.py` |
| Backend routes | `medWatch/api/routes/*.py` |
| Backend auth | `medWatch/api/auth.py`, `middleware.py` |
| Backend storage | `medWatch/api/storage.py` (GCS or local) |
| Backend smoke test | `medWatch/api/tests/smoke_test.py` |
| Frontend entry | `FrontendMedwatch/src/app/layout.tsx` |
| Frontend auth proxy | `FrontendMedwatch/src/app/api/[...slug]/route.ts` |
| Frontend middleware | `FrontendMedwatch/src/middleware.ts` |
| Frontend auth store | `FrontendMedwatch/src/lib/auth-store.ts` |
| Frontend patient store | `FrontendMedwatch/src/lib/store.ts` |
| Frontend SOAP helpers | `FrontendMedwatch/src/lib/patient-format.ts` |
| Architecture diagrams | `medWatch/docs/diagrams/` (18 .drawio + 18 .png) |
| Security audit | `medWatch/docs/SECURITY_AUDIT.md` |

## Cross-anggota integration notes

- **anggota1 (Ghaisan, scraper):** API admin-scrape endpoint mocks the trigger (3s delay, returns cached drug count). Real scraper still runnable manually via `python anggota1/anggota1.py`.
- **anggota2 (Bimo, CRUD):** API patient routes import `pasien_helper.generate_id()` for ID generation (`P001` format). Pasien.json file location is independent (api uses `api/data/patients.json` + GCS).
- **anggota3 (Alia, viz):** API visualization endpoints implement inline data extraction because `BacaData.py:204` has a SyntaxError (`def func() -> dict;` instead of `:`). anggota3 module is not imported.
- **anggota4 (Iqbal, safety):** API drug + safety endpoints wrap `data_loader.py`, `safety_checker.py`, `pencarian_obat.py` directly. Aggregate `severity_score` is computed in the API wrapper from per-drug `skor_risiko`.
- **anggota5 (Abhidal, PDF + auth):** API pdf endpoints inline the SOAP-to-nested schema translation, then call `export_pdf.buat_laporan_pdf()`. The role-based `auth.py` and `tkesehatan_crud.py` files in anggota5 are part of Abhidal's authorized revision (Phase 1 sub-phase).
