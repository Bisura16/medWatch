---
title: MedWatch Install, Deployment, dan Developer Guide
version: 1.0
owner: Ghaisan Khoirul Badruzaman (251524048)
date: 2026-05-18
ticket: W2-D08
---

# MedWatch Install, Deployment, dan Developer Guide

Dokumen ini menjelaskan langkah-langkah pemasangan, pengembangan lokal, dan
deployment untuk seluruh komponen MedWatch:

- Backend Flask di `api/` (deploy ke Google Cloud Run).
- Frontend Next.js 16 di repo `FrontendMedWatch` (deploy ke Vercel).
- Modul desktop CustomTkinter di folder `anggota1/` sampai `anggota5/` plus
  orchestrator `integrasi/`.
- Akuisisi data openFDA via `anggota1/openfda/fetch.py`.

Setiap perintah ditulis dalam bahasa Inggris (CLI standard). Prosa penjelas
ditulis dalam Bahasa Indonesia. Tidak ada nilai kredensial nyata di seluruh
dokumen; semua placeholder ditulis seperti `<your-key-here>` atau
`<random-string>`.

Standar acuan: ISO/IEC/IEEE 26514 untuk dokumentasi user dan developer.

## 1. Prasyarat

### 1.1 Toolchain

| Komponen | Versi yang diuji | Catatan |
|---|---|---|
| Python | 3.13 (development) dan 3.11 (production Cloud Run) | `api/Dockerfile:1` memakai `python:3.11-slim`. Lokal boleh 3.13. |
| Node.js | 22 LTS direkomendasikan | Next.js 16.2.1 mendukung Node 18 sampai 22. Node 25 memicu chunk-emit race yang dicatat sebagai open blocker B-WAVE1-BUILD-1 (lihat bagian Troubleshooting). |
| npm | 10.x atau 11.x (bundle bawaan Node 22) | |
| Git | 2.40+ | |
| Sistem operasi | macOS atau Linux | Homebrew dipakai untuk install tooling tambahan di macOS. |

### 1.2 CLI opsional

| CLI | Kegunaan |
|---|---|
| `gcloud` | Deploy Cloud Run dan mengakses Secret Manager. |
| `vercel` | Deploy frontend ke Vercel dan mengatur environment variable. |
| `gh` | Operasi GitHub via terminal (opsional). |
| `mmdc` | Render diagram Mermaid (kebutuhan dokumentasi, bukan runtime). |
| `pandoc` | Render .docx dari Markdown (kebutuhan dokumentasi). |

### 1.3 Akun cloud

| Resource | Nama | Catatan |
|---|---|---|
| GCP project | `medwatch-polban-2026` | Region default `asia-southeast1`. |
| GCS bucket | `medwatch-polban-2026-state` | Persistensi `users.json` dan `patients.json` saat `USE_CLOUD_STORAGE=true`. |
| Secret Manager | `medwatch-jwt-secret` | Menyimpan nilai `JWT_SECRET` untuk Cloud Run. |
| Cloud Run service | `medwatch-api` | Service name target deploy. |
| Vercel project | `medwatch` | Sudah ter-link di `.vercel/project.json` repo frontend. |

## 2. Clone Repositori

Backend (proyek utama, dimiliki Bimo / GitHub `Bisura16`):

```bash
git clone https://github.com/Bisura16/medWatch.git
cd medWatch
```

Frontend (showcase web, dimiliki Ghaisan / GitHub `Finerium`):

```bash
git clone https://github.com/Finerium/FrontendMedwatch.git FrontendMedWatch
cd FrontendMedWatch
```

Catatan: nama folder lokal frontend bisa berbeda casing-nya dari nama remote
(`FrontendMedwatch` di GitHub vs `FrontendMedWatch` di workstation Ghaisan).
Ini tidak memengaruhi build.

## 3. Backend: Flask API

### 3.1 Setup virtual environment

Dari root repo backend:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r api/requirements.txt
```

Daftar dependensi terverifikasi di `api/requirements.txt:1-11`:

- `Flask==3.1.3`, `Flask-Cors==6.0.0`
- `PyJWT==2.12.0`, `bcrypt==4.2.1`
- `google-cloud-storage==2.18.2`
- `gunicorn==23.0.0`
- `requests==2.33.0`, `beautifulsoup4==4.12.3`
- `matplotlib==3.9.2`, `numpy==1.26.4`
- `fpdf2==2.8.1`

### 3.2 Environment variable

File contoh tersedia di `api/.env.example`. Variabel yang dibaca oleh
`api/config.py:17-37`:

| Nama | Default | Wajib? | Keterangan |
|---|---|---|---|
| `JWT_SECRET` | `dev-only-do-not-use-in-prod` | Wajib di production | Untuk dev lokal boleh pakai string acak apa saja, misalnya `<random-string>`. |
| `PORT` | `8080` | Tidak | Cloud Run override otomatis. |
| `FLASK_DEBUG` | `false` | Tidak | Set `true` saat development local. |
| `GCP_PROJECT_ID` | `medwatch-polban-2026` | Tidak (saat Cloud Run) | |
| `GCS_BUCKET` | `medwatch-polban-2026-state` | Wajib jika `USE_CLOUD_STORAGE=true` | |
| `USE_CLOUD_STORAGE` | `false` | Tidak | Set `true` di Cloud Run untuk pakai bucket. |
| `OPENFDA_API_KEY` | kosong | Disarankan | Tanpa key kuota harian 1.000 request. Dengan key 120.000 request. |
| `CORS_ORIGINS` | hard-coded di `api/config.py:21-25` | Tidak | Allowlist: `https://medwatch-frontend.vercel.app`, `http://localhost:3000`, `http://localhost:5173`. |

Cara mengekspor variabel untuk dev lokal:

```bash
export JWT_SECRET=<random-string>
export FLASK_DEBUG=true
export OPENFDA_API_KEY=<your-key-here>
```

Jangan pernah commit nilai `OPENFDA_API_KEY` atau `JWT_SECRET` ke git. File
`.env*` sudah ditambahkan ke `.gitignore`.

### 3.3 Menjalankan server lokal

Mode development (Flask debug, reload otomatis):

```bash
python -c "from api.app import create_app; create_app().run(host='127.0.0.1', port=8080)"
```

Mode production-like (gunicorn sesuai `api/Dockerfile:23`):

```bash
gunicorn --bind :8080 --workers 2 --threads 4 --timeout 120 api.app:app
```

Verifikasi endpoint health (`api/routes/health.py`):

```bash
curl http://127.0.0.1:8080/api/health
```

Respons yang diharapkan: HTTP 200 dengan body JSON status `ok`.

### 3.4 Smoke test

File `api/tests/smoke_test.py` melakukan 14 assertion (login 3 role, CRUD
pasien SOAP, drug search, safety check, visualisasi, role enforcement).
Jalankan saat server hidup di port 8080:

```bash
python api/tests/smoke_test.py
```

Override base URL untuk testing terhadap Cloud Run:

```bash
BASE_URL=https://<service-url> python api/tests/smoke_test.py
```

## 4. Frontend: Next.js 16 + TypeScript

### 4.1 Install dependensi

Dari root repo frontend:

```bash
nvm use 22  # atau fnm use 22
npm install
```

Versi key di `package.json:26-39`:

- `next 16.2.1`, `react 19.2.4`, `react-dom 19.2.4`
- `typescript ^5`, `tailwindcss ^4`, `eslint-config-next 16.2.1`
- `recharts ^3.8.1`, `framer-motion ^12.38.0`, `zustand ^5.0.12`

### 4.2 Environment variable

Buat file `.env.local` di root repo frontend (tidak ter-commit). Untuk dev
lokal terhadap backend lokal:

```dotenv
BACKEND_API_URL=http://127.0.0.1:8080
```

Untuk production, URL Cloud Run di-set di Vercel project Settings >
Environment Variables (bukan di file lokal yang ter-commit). Variabel ini
hanya tersedia server-side karena tidak diawali `NEXT_PUBLIC_`. Browser
hanya berkomunikasi dengan domain Vercel; Vercel API proxy di
`src/app/api/[...slug]/route.ts:11` meneruskan request ke Cloud Run.

### 4.3 Menjalankan server lokal

Mode development:

```bash
npm run dev
```

`next dev` akan listen di `http://localhost:3000`. Di environment Node 22
LTS, command ini memakai bundler default (Turbopack). Jika Anda berada di
Node 25 dan terkena blocker B-WAVE1-BUILD-1, paksa webpack:

```bash
npx next dev --webpack
```

Mode production-like:

```bash
npm run build
npm run start
```

`npm run build` memerlukan Node 22 LTS untuk build yang konsisten dengan
Vercel.

## 5. Modul Desktop CustomTkinter

Setiap modul anggota dapat dijalankan independen. Modul ini dimaksudkan
sebagai deliverable desktop utama (lihat `CLAUDE.md` Rule 5: web stack
adalah supplementary showcase, bukan pengganti).

### 5.1 Menjalankan modul tunggal

```bash
# Modul auth + role menu (anggota5)
python anggota5/main_anggota5.py

# Modul scraping data obat (anggota1)
python anggota1/anggota1.py

# Modul CRUD pasien SOAP (anggota2)
python anggota2/main_anggota2.py

# Modul visualisasi matplotlib (anggota3)
python anggota3/main_anggota3.py

# Modul drug safety check (anggota4)
python anggota4/main_anggota4.py
```

### 5.2 Menjalankan integrator desktop terpadu

Folder `integrasi/` menyatukan modul anggota1 sampai anggota5 lewat
adapter, tanpa memodifikasi file teman satu pun. Detail di
`integrasi/README.md`.

```bash
python integrasi/app_terpadu.py
```

`integrasi/adapter.py` melakukan panggilan ke setiap modul via import
langsung atau subprocess. File anggota1-5 tetap read-only sesuai kontrak
tim (lihat `CLAUDE.md` Rule 2).

Demo credentials untuk uji manual (terdokumentasi di
`integrasi/README.md:13-18`):

| Role | Username | Password (placeholder dokumen) |
|---|---|---|
| Admin | `admin1` | tersimpan di `anggota5/data/users.json` setelah hashing |
| Tenaga Kesehatan | `bidan1` | sama |

Nilai password lengkap tidak ditulis di dokumen ini sesuai aturan anti-leak
kredensial.

## 6. Akuisisi Data openFDA

Pipeline ini menggantikan scraping drugs.com yang diblokir oleh proteksi
Akamai per Mei 2026 (rujuk ADR-0004 dan `anggota1/scraper.log`). Tidak ada
upaya anti-bot bypass.

### 6.1 Mendapatkan API key

1. Buka `https://open.fda.gov/apis/authentication/`.
2. Daftarkan email dan tunggu email konfirmasi (gratis, instan).
3. Salin nilai API key dari email tersebut.
4. Export ke environment variable:

```bash
export OPENFDA_API_KEY=<your-key-here>
```

Kuota dengan key: 240 request per menit dan 120.000 request per 24 jam per
IP. Tanpa key: 1.000 request per 24 jam. Nilai key tidak boleh dicetak,
dilog, atau di-commit; modul fetch akan mengganti tampilan dengan
`<redacted>` di seluruh log dan field `source_url`.

### 6.2 Menjalankan pipeline

Dari root repo backend, dengan `.venv` aktif:

```bash
python -m anggota1.openfda.fetch --max-recall-pages 6
```

Output ditulis ke:

- `anggota1/data/drug_safety_data.json` (FAERS adverse events agregat per
  obat, 74 obat curated dari WHO Essential Medicines List 2023 dan
  formularium BPOM Faskes 1).
- `anggota1/data/drug_recalls.json` (FDA enforcement recalls, sort
  newest-first).

CLI flag lengkap (referensi `anggota1/openfda/fetch.py:475-491`):

| Flag | Default | Keterangan |
|---|---|---|
| `--drugs FILE` | bundled 74 obat | File newline-separated daftar obat. |
| `--max-drugs N` | `0` (no cap) | Cap jumlah obat. |
| `--max-recall-pages N` | `26` | Maks halaman recall (1 halaman = 1000 record). |
| `--skip-events` | off | Skip pull FAERS. |
| `--skip-recalls` | off | Skip pull recall. |
| `--log-level` | `INFO` | DEBUG/INFO/WARNING. |

Verifikasi hasil:

```bash
ls -lh anggota1/data/drug_safety_data.json anggota1/data/drug_recalls.json
python -c "import json; d=json.load(open('anggota1/data/drug_safety_data.json')); print('drugs:', len(d))"
python -c "import json; d=json.load(open('anggota1/data/drug_recalls.json')); print('recalls:', len(d))"
```

Hasil acquisition terakhir (Wave 1, lihat `.mission/state.json`): 74 drug
records dan 1.850 reaction term, 6.000 recall records.

## 7. Deployment Backend ke Cloud Run

### 7.1 Prasyarat

1. `gcloud` CLI terinstall dan ter-auth dengan akun GCP
   `ghaisan.khoirul.b@gmail.com`.
2. Project aktif `medwatch-polban-2026`:
   ```bash
   gcloud config set project medwatch-polban-2026
   gcloud config set run/region asia-southeast1
   ```
3. Service Account default Cloud Run sudah punya role:
   - `roles/storage.objectAdmin` pada bucket `medwatch-polban-2026-state`.
   - `roles/secretmanager.secretAccessor` pada secret
     `medwatch-jwt-secret`.
4. Bucket `medwatch-polban-2026-state` sudah ada (provisioned di Wave 0).
5. Secret `medwatch-jwt-secret` sudah berisi nilai versi `latest`
   (provisioned di Wave 0; nilai aktualnya hanya hidup di Secret Manager).

### 7.2 Deploy

Sebelum deploy, catat state pre-change (rev ID, env, traffic split) untuk
guardrail rollback per `CLAUDE.md` Mission Protocol section:

```bash
gcloud run services describe medwatch-api --region asia-southeast1 \
  --format="value(status.latestReadyRevisionName,status.url)"
```

Deploy from source (Cloud Build memakai `api/Dockerfile`):

```bash
gcloud run deploy medwatch-api \
  --source api/ \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --set-env-vars=USE_CLOUD_STORAGE=true,GCS_BUCKET=medwatch-polban-2026-state \
  --update-secrets=JWT_SECRET=medwatch-jwt-secret:latest
```

### 7.3 Verifikasi post-deploy

Ambil URL service yang baru:

```bash
SERVICE_URL=$(gcloud run services describe medwatch-api --region asia-southeast1 \
  --format="value(status.url)")
curl -sS "$SERVICE_URL/api/health"
```

Respons harus HTTP 200. Lanjut smoke test penuh:

```bash
BASE_URL="$SERVICE_URL" python api/tests/smoke_test.py
```

Jika regresi terjadi, rollback ke revisi yang dicatat sebelumnya:

```bash
gcloud run services update-traffic medwatch-api \
  --region asia-southeast1 \
  --to-revisions=<previous-revision-name>=100
```

## 8. Deployment Frontend ke Vercel

### 8.1 Prasyarat

1. `vercel` CLI terinstall dan ter-auth ke akun `finerium`.
2. Project sudah ter-link (file `.vercel/project.json` ada di repo
   frontend).
3. Environment variable `BACKEND_API_URL` sudah di-set di Vercel project
   Settings untuk scope yang sesuai (Production, Preview, Development).
   Nilainya adalah URL Cloud Run dari langkah 7.3; nilai aktual tidak
   ditulis di dokumen ini.

### 8.2 Set environment variable

Via CLI (interactive, akan minta value tanpa menyimpan ke shell history
dalam file):

```bash
vercel env add BACKEND_API_URL production
vercel env add BACKEND_API_URL preview
vercel env add BACKEND_API_URL development
```

Pull env ke local untuk dev (tanpa commit):

```bash
vercel env pull .env.local
```

### 8.3 Deploy

Preview deployment (URL acak per push):

```bash
vercel
```

Production deployment ke `medwatch-frontend.vercel.app`:

```bash
vercel --prod
```

### 8.4 Verifikasi post-deploy

Ganti `<vercel-url>` dengan URL output `vercel --prod`.

```bash
curl -I https://<vercel-url>/login
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"bidan_siti","password":"<placeholder>"}' \
  https://<vercel-url>/api/auth/login
```

Login lewat proxy harus mengembalikan JSON dengan `token` dan `user.role`
sesuai akun seed.

## 9. Troubleshooting

### 9.1 Node 25 + Next.js 16: chunk-emit race

Gejala: `npm run build` selesai tanpa error namun `.next/server/app/<route>/page.js`
dan `.next/static/chunks/` kosong. SSR pages mengembalikan HTTP 500 dengan
`InvariantError: Could not find the module ... in the React Client Manifest`.
Dev mode kadang juga gagal serve API proxy dengan `ENOENT pages-manifest.json`.

Akar masalah: Node 25.x di luar supported range Next.js 16.2.1 (18 sampai
22 LTS). Detail di `.mission/state.json` open blocker `B-WAVE1-BUILD-1`.

Solusi:

```bash
nvm install 22
nvm use 22
rm -rf .next node_modules
npm install
npm run build && npm run start
```

Alternatif dengan `fnm`:

```bash
fnm install 22
fnm use 22
```

Vercel hosting tidak terdampak karena memakai Node 22 LTS by default.

### 9.2 drugs.com HTTP 403 (Akamai block)

Gejala: setiap request scraping ke `drugs.com` mengembalikan HTTP 403.
Bukti di `anggota1/scraper.log`.

Solusi: pakai pipeline openFDA per ADR-0004 (`docs/adr/0004-drugs-com-akamai-to-openfda-pivot.md`).
Tidak melakukan bypass anti-bot karena melanggar ToS drugs.com.

### 9.3 pyenv / Homebrew Python collision

Gejala: `which python3` menunjuk ke interpreter yang berbeda dari
`.venv/bin/python` setelah `source .venv/bin/activate`. Dependensi
ter-install ke site-packages global, bukan venv.

Solusi:

```bash
deactivate 2>/dev/null
hash -r
python3.13 -m venv .venv
source .venv/bin/activate
which python  # harus menunjuk ke .venv/bin/python
pip install -r api/requirements.txt
```

Jika `python3.13` tidak ada, install via Homebrew:

```bash
brew install python@3.13
```

### 9.4 Cloud Run cold start 500 error

Gejala: request pertama setelah idle panjang mengembalikan 500. Request
berikutnya berhasil.

Penjelasan: cold start menginisialisasi Flask app dan client `google-cloud-storage`.
Untuk demo, panaskan service dengan polling `/api/health` selama 1 menit
sebelum demo presentasi.

### 9.5 CORS preflight failure dari domain non-allowlist

Gejala: browser console menampilkan `Access-Control-Allow-Origin` mismatch.

Penjelasan: allowlist hard-coded di `api/config.py:21-25`. Hanya
`medwatch-frontend.vercel.app`, `localhost:3000`, `localhost:5173` yang
diizinkan akses langsung. Frontend production memakai Vercel API proxy
(`src/app/api/[...slug]/route.ts`) sehingga browser tidak pernah CORS ke
Cloud Run.

### 9.6 `OPENFDA_API_KEY` tidak terdeteksi

Gejala: log fetch mengeluarkan `OPENFDA_API_KEY not set; falling back to
unauthenticated quota` (`anggota1/openfda/fetch.py:505`).

Solusi:

```bash
echo "OPENFDA_API_KEY length=${#OPENFDA_API_KEY}"
```

Jika length 0, re-export variable di shell yang sama sebelum menjalankan
fetch module.

## 10. Pengecekan Kelengkapan (Smoke Checks)

Daftar minimum yang harus PASS sebelum demo presentasi dosen.

### 10.1 Backend lokal

```bash
curl http://127.0.0.1:8080/api/health
# expect: HTTP 200, body {"status":"ok",...}

python api/tests/smoke_test.py
# expect: 14 assertion OK, exit code 0
```

### 10.2 Frontend lokal (saat backend lokal hidup)

```bash
curl -I http://localhost:3000/login
# expect: HTTP 200

curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"bidan_siti","password":"<placeholder>"}' \
  http://localhost:3000/api/auth/login
# expect: HTTP 200, body {"token":"<jwt>","user":{"role":"tenaga_kesehatan",...}}
```

### 10.3 Cloud Run production

```bash
SERVICE_URL=$(gcloud run services describe medwatch-api --region asia-southeast1 \
  --format="value(status.url)")
curl -sS "$SERVICE_URL/api/health"
BASE_URL="$SERVICE_URL" python api/tests/smoke_test.py
```

### 10.4 Vercel production

```bash
curl -I https://medwatch-frontend.vercel.app/login
# expect: HTTP 200

curl -I https://medwatch-frontend.vercel.app/admin
# expect: HTTP 200 (redirect ke /login jika tidak ada cookie)
```

### 10.5 Desktop terpadu

```bash
python integrasi/app_terpadu.py
# expect: login prompt, role-based menu sesuai user yang login
```

## 11. Referensi

- `api/Dockerfile`: runtime container backend (Python 3.11-slim, gunicorn).
- `api/config.py:17-37`: semua env var yang dibaca backend.
- `api/app.py`: registrasi blueprint Flask dan CORS.
- `api/tests/smoke_test.py`: 14 assertion end-to-end.
- `anggota1/openfda/fetch.py`: pipeline akuisisi openFDA.
- `anggota1/openfda/README.md`: dokumentasi singkat schema openFDA.
- `package.json:26-39`: dependensi frontend pin version.
- `next.config.ts`: konfigurasi Next.js.
- `src/app/api/[...slug]/route.ts`: Vercel API proxy ke Cloud Run.
- `integrasi/README.md`: deskripsi orchestrator desktop.
- `.mission/state.json`: state mission, termasuk blocker B-WAVE1-BUILD-1.
- `docs/adr/0004-drugs-com-akamai-to-openfda-pivot.md`: ADR pivot scraping ke openFDA.
- `docs/SECURITY.md`: threat model lengkap (W2-D10).
- `docs/API.md`: kontrak endpoint backend (W2-D06).
- `docs/AS-BUILT.md`: dokumen As-Built post-Wave-1 (W2-D11).

## 12. Catatan Hak Akses dan Keamanan

- Tidak ada nilai kredensial (API key, password, JWT secret, service-account
  JSON) yang ditulis di dokumen ini. Resource NAMES (project, bucket,
  secret name, service name) dicantumkan karena bukan secret.
- Akun `dudungdotnet@gmail.com` adalah email pelanggan akhir yang dilarang
  disentuh dalam operasi otomatis apa pun (lihat `CLAUDE.md` Mission
  Protocol).
- Operasi `git push`, `git push --force`, dan `git reset --hard` tidak
  diizinkan tanpa instruksi eksplisit dari Ghaisan. Cloud Run dan Vercel
  redeploy diizinkan saat misi memerlukan, dengan guardrail rollback yang
  ada di section 7.3.
