---
title: MedWatch Security and Threat Model
version: 1.0
owner: Ghaisan Khoirul Badruzaman (NIM 251524048, Project Leader Kelompok B5)
date: 2026-05-18
status: As-Built (post-Wave-1)
references:
  - OWASP Top 10 (2021 edition, owasp.org/Top10/)
  - Microsoft STRIDE threat-modeling framework
  - NIST SP 800-63B (digital identity, password hashing guidance)
  - OWASP ASVS v4.0.3 (informational)
related_docs:
  - docs/SECURITY_AUDIT.md (Wave 1 hands-on audit, 2026-05-04)
  - docs/SDD.md (design viewpoints)
  - docs/AS-BUILT.md (deviations table)
---

# Security and Threat Model MedWatch

Dokumen ini menjabarkan postur keamanan sistem MedWatch pada titik pengiriman tugas akhir Proyek 1 Pengembangan Perangkat Lunak Desktop kepada dosen Politeknik Negeri Bandung pada 25 Mei 2026. Cakupan: aplikasi desktop modul `anggota1..anggota5/`, integration layer Flask di `api/`, frontend Next.js di repo `FrontendMedWatch/`, deployment Cloud Run + Vercel, dan jalur data scraping openFDA.

Dokumen ini melengkapi `docs/SECURITY_AUDIT.md` (audit Wave 1 tanggal 4 Mei 2026) dengan pemetaan formal terhadap OWASP Top 10 (2021) dan tabel STRIDE per aset. Klaim teknis dirujuk ke file:line aktual dalam repositori; tidak ada kontrol yang diklaim tanpa basis kode yang dapat diverifikasi.

---

## 1. Lingkup dan Audiens

### 1.1 Lingkup keamanan

| Komponen | Lokasi | Termasuk |
|---|---|---|
| Backend integration layer | `api/` | Auth, RBAC middleware, routes Patient/Drug/Safety/Admin/PDF/Visualization, storage |
| Modul mahasiswa | `anggota1/`..`anggota5/` | Desktop CustomTkinter (read-only oleh mission), dipanggil via `api/bootstrap.py` |
| Frontend showcase | `FrontendMedWatch/` | Next.js 15 App Router, proxy edge, RBAC middleware client side |
| Deployment cloud | Cloud Run `medwatch-api` + Vercel `medwatch-frontend` | Container image, env, IAM, jaringan |
| Data scraping openFDA | `anggota1/openfda/fetch.py` | Pengambilan adverse-events + recall via `api.fda.gov` |

Out of scope: hardening tingkat produksi klinis (HIPAA, UU PDP 2022), audit pen-test eksternal, WAF custom, dan rotasi kunci otomatis. Item-item ini disurfacing di Section 7 (Residual Risk) dan dijabarkan rinci pada `ProductionGrade-ImplementationPlan/04-hardening-plan.md`.

### 1.2 Audiens

| Pembaca | Bagian yang harus dibaca |
|---|---|
| Developer (anggota tim) | 1, 4, 5, 8 (cara berkontribusi aman) |
| Quality Assurance (Bimo) | 4, 5, 6 (apa yang harus diuji) |
| System administrator (Ghaisan) | 6, 8, 9 (postur cloud + checklist demo) |
| Dosen pendamping | 1, 2, 6, 7 (ringkasan postur + batasan jujur) |

### 1.3 Klasifikasi data

MedWatch versi presentasi memproses **data sintetik demo**, bukan PHI (Protected Health Information) sebenarnya. Klasifikasi internal:

- `confidential`: hash password, JWT signing key, openFDA API key.
- `internal`: data pasien SOAP sintetik di `api/data/patients.json` dan `anggota2/Pasien.json`.
- `public`: katalog obat (`anggota4/data/drug_database.json`), data scraping openFDA (`anggota1/data/*.json`).

---

## 2. Aset yang Dilindungi

| ID | Aset | Lokasi penyimpanan | Sensitivitas | Pemilik kontrol |
|---|---|---|---|---|
| A1 | JWT signing key | GCP Secret Manager, nama secret `medwatch-jwt-secret` (resource name OK; nilai tidak pernah keluar dari Secret Manager) | confidential | Cloud Run service account |
| A2 | Patient PII SOAP | `api/data/patients.json` (lokal) dan `gs://medwatch-polban-2026-state/patients.json` (cloud); berisi nama, alamat, riwayat kesehatan, diagnosa | confidential (sintetik demo) | Backend Flask + JWT |
| A3 | openFDA API key | Environment variable `OPENFDA_API_KEY` (Cloud Run env, lokal `.env.local`); dibaca di `api/config.py:34` dan `anggota1/openfda/fetch.py:501` | confidential | OS env / Cloud Run revision |
| A4 | User credentials (bcrypt hash) | `api/data/users.json` (lokal) dan `gs://medwatch-polban-2026-state/users.json` (cloud); field `password_hash`, cost 12 | confidential | Backend Flask |
| A5 | Scraped data openFDA | `anggota1/data/drug_safety_data.json`, `anggota1/data/drug_recalls.json` | public (data publik FDA) | Backend + scraper job |
| A6 | Session token | Cookie `medwatch_token`, httpOnly + Secure + SameSite=Lax, max-age 12 jam; di-set oleh `src/app/api/[...slug]/route.ts:82` | confidential | Browser + proxy Vercel |
| A7 | Audit/operational logs | stdout Cloud Run -> Cloud Logging (otomatis); format Python `logging` di `api/app.py:20` | internal | Cloud Logging |

Resource names yang digunakan dokumen ini (project `medwatch-polban-2026`, bucket `medwatch-polban-2026-state`, service `medwatch-api`, secret `medwatch-jwt-secret`) adalah identifier publik yang aman dicantumkan sesuai mission constraint 12; nilai kredensial sama sekali tidak ada.

---

## 3. Aktor dan Sumber Ancaman

| ID | Aktor | Motivasi | Kapabilitas | Vektor |
|---|---|---|---|---|
| T1 | Script kiddie eksternal | Defacing, fun | Tool scan otomatis (Nikto, sqlmap), payload OWASP umum | HTTP terhadap `medwatch-frontend.vercel.app` |
| T2 | Bot otomatis (crawler, brute force) | Kompromi akun, scraping | Pendaftaran user agent palsu, request volume tinggi | HTTP terhadap `/api/auth/login` |
| T3 | User terdaftar yang ingin escalate role | Akses fitur admin, lihat data pasien lain | Token JWT valid, bisa modifikasi request | Manipulasi payload, body request, header |
| T4 | Supply chain | Inject payload via dependency npm/pip | Publikasi paket trojan, typosquatting | `package.json`, `api/requirements.txt` |
| T5 | Insider (anggota tim) | Penasaran, demo bug yang tidak disengaja | Akses repo, kredensial demo, akun GCP free tier | Commit langsung ke main, akses console GCP |
| T6 | Dosen/penguji saat presentasi | Verifikasi klaim keamanan via percobaan input | Akses penuh sebagai user demo | UI standar |

Asumsi: aktor di luar tim tidak memiliki akses fisik ke mesin pengembang (laptop Ghaisan), tidak memiliki Owner role di project `medwatch-polban-2026`, dan tidak memiliki shell di container Cloud Run.

---

## 4. Pemetaan OWASP Top 10 (2021)

Sumber kategori: OWASP Top 10:2021 (owasp.org/Top10/). Setiap baris berisi Risk Statement, Project Mitigation (dengan kutipan file:line aktual), dan Residual Risk.

### A01 Broken Access Control

- **Risk:** User dapat mengakses fungsi atau data yang seharusnya hanya untuk role lain (mis. masyarakat membaca pasien lain, tenaga_kesehatan memicu scraper admin).
- **Mitigation:**
  - Backend RBAC: dekorator `@require_auth` dan `@require_role(*allowed_roles)` di `api/middleware.py:17` dan `api/middleware.py:37`. Tiap admin endpoint melalui `@require_role("admin")`, contoh `api/routes/admin_routes.py:22` (scrape), `api/routes/admin_routes.py:42` (list users), `api/routes/admin_routes.py:49` (create user).
  - Patient ownership check: `api/routes/patient_routes.py:157` menolak masyarakat melihat record yang `owner_username` bukan miliknya (HTTP 403).
  - Frontend RBAC: proxy edge di `src/proxy.ts:65` me-redirect non-admin yang mengakses `/admin/*` ke landing role mereka; matcher di `src/proxy.ts:86`.
  - Backend re-check (defense in depth): walaupun proxy frontend bisa di-bypass dengan menyerang Cloud Run langsung, decorator `@require_role` di backend tetap menolak (HTTP 403). Bukti: `api/middleware.py:43`.
- **Residual Risk:** Bypass proxy Vercel ke Cloud Run secara langsung secara teknis mungkin karena service dikonfigurasi `--allow-unauthenticated`. Mitigasi efektif dilakukan oleh RBAC backend di atas; lihat catatan L2 di `docs/SECURITY_AUDIT.md`.

### A02 Cryptographic Failures

- **Risk:** Kebocoran rahasia, hashing lemah, transport tanpa TLS.
- **Mitigation:**
  - bcrypt cost 12 untuk hashing password: `api/auth.py:12`. Cost 12 merupakan default yang aman per OWASP Password Storage Cheat Sheet.
  - JWT HS256 dengan secret dari env `JWT_SECRET`: `api/auth.py:32` dan `api/config.py:17`. Secret produksi disimpan di Secret Manager `medwatch-jwt-secret`; dev secret rotated terpisah (tidak pernah commit nilai).
  - Issuer claim `iss=medwatch-api` di-issue (`api/auth.py:31`) dan di-validate (`api/auth.py:37`) untuk menolak token dari issuer tidak dikenal.
  - Cookie httpOnly + Secure + SameSite=Lax di-set oleh proxy Vercel: `src/app/api/[...slug]/route.ts:82` dengan `httpOnly: true`, `secure: process.env.NODE_ENV === "production"`, `sameSite: "lax"`, `maxAge: 12*60*60`.
  - TLS: Cloud Run dan Vercel mengelola sertifikat otomatis (Let's Encrypt). Tidak ada endpoint plain HTTP di production.
  - Hash password tidak pernah keluar dari API: `api/helpers.py:16` `strip_password_fields` dipanggil di `api/routes/admin_routes.py:45` dan `api/routes/admin_routes.py:85`.
- **Residual Risk:** JWT HS256 menggunakan secret simetris; rotasi belum otomatis (lihat Section 7 Item R4). JWT yang sudah issued tidak dapat di-revoke server-side sebelum expiry (mitigasi: expiry 12 jam, cookie cleared on logout).

### A03 Injection

- **Risk:** Eksekusi kode/SQL/perintah dari input user.
- **Mitigation:**
  - Tidak ada SQL: storage adalah file JSON dibaca via `json.load` di `api/storage.py:35`. Tidak ada string interpolation ke query.
  - Tidak ada `eval()` atau `exec()` di `api/`. Verifikasi: `grep -rn "eval(\|exec(" api/` tidak menghasilkan match (selain identifier seperti `execute` dalam framework).
  - Input parsing aman: semua route menerima JSON via `request.get_json(silent=True)`; tidak ada `request.form` yang di-render kembali sebagai HTML. Contoh: `api/routes/auth_routes.py:15`, `api/routes/patient_routes.py:165`.
  - Validasi range medical fields: `api/routes/patient_routes.py:56` `_validate_medical_ranges` membatasi tipe dan rentang sebelum dipersist.
  - Patient ID format `P\d{3}` di-generate server-side di `api/routes/patient_routes.py:102`, bukan dipasok user.
  - Frontend: React auto-escaping default; tidak ada `dangerouslySetInnerHTML` di route aktif.
- **Residual Risk:** PDF generator menerima string dari user (nama pasien, riwayat) yang di-passing ke fpdf2; fpdf2 tidak mengeksekusi HTML/JS, namun karakter non-Latin1 perlu di-encode (lihat fpdf2 changelog). Tidak ada CVE aktif terhadap fpdf2 2.8.1.

### A04 Insecure Design

- **Risk:** Cacat arsitektur fundamental yang tidak bisa ditambal oleh patch.
- **Mitigation:**
  - **Pattern B (server-side proxy):** browser hanya melihat domain Vercel; backend Cloud Run URL disimpan di env `BACKEND_API_URL` (server-only, tidak diawali `NEXT_PUBLIC_`). Proxy: `src/app/api/[...slug]/route.ts:11` membaca `BACKEND` lalu fetch upstream di line 52. JWT dari cookie httpOnly di-attach sebagai header Authorization di `src/app/api/[...slug]/route.ts:41`, bukan diekspos ke JavaScript browser.
  - JWT di httpOnly cookie (XSS-resistant); tidak ada `localStorage.setItem("token", ...)` di kode frontend yang aktif.
  - CORS allowlist eksplisit (bukan `*`): `api/config.py:21`-`25` membatasi origin ke domain Vercel + localhost dev.
  - Decorator-based RBAC (Section A01) memaksa setiap route menyatakan policy aksesnya; tidak ada default-allow.
- **Residual Risk:** Tidak ada CSRF token untuk state-changing route. Risiko CSRF dimitigasi oleh cookie SameSite=Lax + same-origin request (browser hanya request Vercel domain ke Vercel API route), namun bukan mitigasi setara CSRF token. Lihat Section 7 Item R3.

### A05 Security Misconfiguration

- **Risk:** Debug mode aktif di produksi, header bocor, default credential, CORS terlalu permisif.
- **Mitigation:**
  - `FLASK_DEBUG=false` di Cloud Run env (`api/config.py:37`).
  - Custom error handler 500 mengembalikan pesan generik `"internal server error"` tanpa stack trace: `api/app.py:53`.
  - Header `Server` di-strip oleh `@app.after_request` di `api/app.py:58`.
  - CORS allowlist eksplisit: `api/config.py:21`.
  - Secret bukan inline di kode; via env: `api/config.py:17` (`JWT_SECRET`), `api/config.py:34` (`OPENFDA_API_KEY`).
  - `.gitignore` backend mencegah commit `.env`, `.env.*`, `*.pem`, `*.key`, `service-account*.json`, `gcp-key*.json` (lihat `.gitignore:18`-`28`). `.gitignore` frontend mengecualikan `.env*` dan `*.pem` (`FrontendMedWatch/.gitignore:25`, `.gitignore:34`).
- **Residual Risk:** Endpoint `/api/info` publik dan mengungkap modul mana yang ter-load; informasi minor implementation detail.

### A06 Vulnerable and Outdated Components

- **Risk:** Dependency dengan CVE diketahui.
- **Mitigation:**
  - Versi backend di-pin: `api/requirements.txt:1`-`11` (Flask 3.1.3, Flask-Cors 6.0.0, PyJWT 2.12.0, bcrypt 4.2.1, google-cloud-storage 2.18.2, gunicorn 23.0.0, requests 2.33.0, beautifulsoup4 4.12.3, matplotlib 3.9.2, numpy 1.26.4, fpdf2 2.8.1).
  - Versi frontend di-pin di `FrontendMedWatch/package.json` (Next.js 16.2.1, React 19.2.4, dst.).
  - Hasil `pip-audit -r api/requirements.txt` post-remediation Wave 1: "No known vulnerabilities found" (bukti di `docs/SECURITY_AUDIT.md` Section pip-audit).
- **Residual Risk:** Tidak ada CI yang menjalankan `pip-audit` / `npm audit` otomatis di setiap PR; audit dijalankan manual oleh `security-analyst` agent (lihat Wave 4). Frontend memiliki 3 high vulns yang terisolasi pada `_archived/` paths (H5, H6, H7 di `docs/SECURITY_AUDIT.md`).

### A07 Identification and Authentication Failures

- **Risk:** Lemah kepada credential stuffing, brute force, session fixation.
- **Mitigation:**
  - JWT issuer claim di-validate: `api/auth.py:37` `jwt.decode(..., issuer="medwatch-api")`.
  - JWT expiry 12 jam (`api/config.py:19`); claim `exp` di-issue (`api/auth.py:29`) dan otomatis diperiksa oleh PyJWT saat decode.
  - Login error message generik (`"invalid credentials"`) untuk user tidak ada dan password salah: `api/routes/auth_routes.py:37` dan `api/routes/auth_routes.py:40`, mencegah account enumeration.
  - Logout cookie cleared: `src/app/api/[...slug]/route.ts:96`.
  - Tidak ada parameter "remember me" yang memperpanjang session.
- **Residual Risk:** **Belum ada rate limit / account lockout** pada `/api/auth/login`; secara teori serangan brute force memungkinkan walaupun bcrypt cost 12 (sekitar 100 ms per attempt) memperlambat throughput. Lihat Section 7 Item R1. Mitigasi platform: Cloud Run rate-limit per region otomatis, dan Vercel edge melindungi dari volume sangat tinggi.

### A08 Software and Data Integrity Failures

- **Risk:** Insecure deserialization, supply-chain tanpa verifikasi integrity.
- **Mitigation:**
  - Tidak ada `pickle.load`, `yaml.load` (tanpa SafeLoader), atau JSON-from-untrusted-source di kode `api/`. Storage hanya menerima JSON yang ditulis oleh service sendiri.
  - Dependency lock file: `api/requirements.txt` dengan versi exact (`==`); `package-lock.json` (frontend) memuat integrity hashes SHA-512 per resolved package.
  - Build chain: container image Cloud Run di-build via Cloud Build dari Dockerfile (`api/Dockerfile`), tidak ada `:latest` tag bersifat mutable untuk image production (revision tag terkunci).
  - Atomic write untuk JSON file: penulisan via `_save_local` di `api/storage.py:38` membuka file mode `w` dengan `json.dump`; pola tulis-temporary-then-rename TIDAK diterapkan saat ini (lihat Residual Risk).
- **Residual Risk:** Penulisan `patients.json` dan `users.json` tidak atomic (tidak ada `write-temp + os.rename`); race kondisi crash bisa meninggalkan file korup. Mitigasi: GCS object versioning otomatis menyimpan revisi sebelumnya untuk recovery. Signed packages (Sigstore, npm provenance) tidak diverifikasi.

### A09 Security Logging and Monitoring Failures

- **Risk:** Insiden tidak terdeteksi karena log buruk atau hilang.
- **Mitigation:**
  - Logging tersentralisasi via stdlib Python `logging` di-init `api/app.py:20` level INFO format `%(asctime)s %(levelname)s %(name)s: %(message)s`.
  - Login success/failure di-log dengan username (bukan password): `api/routes/auth_routes.py:27`, `api/routes/auth_routes.py:36`, `api/routes/auth_routes.py:39`. Password tidak pernah di-log (verifikasi grep tidak menemukan `logger.*password`).
  - Role-denied di-log: `api/middleware.py:44`.
  - Admin actions di-log dengan aktor: `api/routes/admin_routes.py:26` (scrape), `api/routes/admin_routes.py:84` (create user), `api/routes/admin_routes.py:102` (delete user).
  - Cloud Run secara otomatis mem-forward stdout ke Cloud Logging dengan project-level retention default 30 hari.
- **Residual Risk:** Tidak ada audit trail yang dipersist ke storage tahan lama (durable) selain Cloud Logging; tidak ada SIEM atau alerting threshold (mis. >5 login fail/menit -> alert). Lihat Section 7 Item R2.

### A10 Server-Side Request Forgery (SSRF)

- **Risk:** Backend membuat HTTP request ke URL yang dikendalikan user (memungkinkan akses ke metadata service GCP, internal network).
- **Mitigation:**
  - Tidak ada parameter user yang menjadi target URL `requests.get`. Verifikasi: satu-satunya pemanggil `requests.get` di backend adalah `anggota1/openfda/fetch.py` yang menggunakan konstanta hard-coded `EVENT_ENDPOINT = "https://api.fda.gov/drug/event.json"` (`anggota1/openfda/fetch.py:56`) dan `ENFORCEMENT_ENDPOINT = "https://api.fda.gov/drug/enforcement.json"` (`anggota1/openfda/fetch.py:57`).
  - Proxy Vercel meneruskan ke konstanta `BACKEND_API_URL` env, tidak ke URL yang dipasok client: `src/app/api/[...slug]/route.ts:11`-`29`.
  - Scraper anggota1 dipicu mock (sleep + return cached count) di production demo: `api/routes/admin_routes.py:27`, bukan inline Selenium yang menerima URL eksternal.
- **Residual Risk:** Jika di masa depan endpoint admin scraper diaktifkan inline dengan parameter URL, mitigasi ini perlu di-re-evaluate.

---

## 5. STRIDE per Aset

STRIDE (Microsoft): Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege. Tabel berikut memetakan setiap kategori STRIDE terhadap aset utama dengan kontrol nyata dan residual risk per baris.

### 5.1 A1 JWT signing key

| STRIDE | Ancaman | Mitigasi nyata (file:line) | Residual |
|---|---|---|---|
| S | Forge JWT dengan kunci tebakan | HS256 dengan secret dari Secret Manager (`api/config.py:17`); issuer claim required (`api/auth.py:37`). | Secret produksi di Secret Manager terhindar dari exfiltrasi; akses dibatasi service account Cloud Run. |
| T | Mutasi payload token tanpa update signature | HMAC signature otomatis di-verify oleh `jwt.decode` (`api/auth.py:37`); mutasi gagal validasi. | None signifikan. |
| R | Tidak bisa membuktikan token sudah issued oleh server | Log line `login ok: {username} as {role}` di `api/routes/auth_routes.py:27` + `iat` claim. | Log lifetime 30 hari (Cloud Logging default). |
| I | Disclosure secret di log/error | Secret tidak pernah di-log; error handler generik (`api/app.py:53`). | Secret bisa terlihat di `gcloud secrets versions access` -> akses dibatasi IAM. |
| D | Secret rusak/hilang | Secret Manager menyimpan versi historis; rollback ke versi lama mungkin. | Tidak ada rotasi otomatis (R4). |
| E | Token dengan role escalated | Role di-check ulang di backend per endpoint (`api/middleware.py:43`); proxy frontend bukan satu-satunya gate. | None signifikan untuk single secret; kunci dicompromise akan mempengaruhi seluruh token (lihat R4). |

### 5.2 A2 Patient PII SOAP

| STRIDE | Ancaman | Mitigasi nyata (file:line) | Residual |
|---|---|---|---|
| S | User palsu masuk dan baca data pasien | `@require_role("tenaga_kesehatan", "admin")` di list (`api/routes/patient_routes.py:135`) dan create (`api/routes/patient_routes.py:163`); ownership check di get (`api/routes/patient_routes.py:157`). | Bypass via proxy Vercel ditangkap di backend re-check. |
| T | Mutasi data via API tanpa hak | PUT `/api/patients/<pid>` membutuhkan role tenaga_kesehatan/admin (`api/routes/patient_routes.py:191`); validation `_validate_medical_ranges` (`api/routes/patient_routes.py:56`) mencegah injeksi data tidak masuk akal. | File JSON tidak atomic (lihat A08 residual). GCS versioning untuk rollback. |
| R | Tidak ada bukti siapa yang mengubah record | `created_by` di-stamp pada create (`api/routes/patient_routes.py:183`); log line per CRUD (`api/routes/patient_routes.py:186`, `api/routes/patient_routes.py:216`). | Tidak ada `updated_by` / `updated_at` history per field (R2). |
| I | Exposure di response, PDF, atau log | `password_hash` tidak relevan pada pasien; SOAP data hanya dikembalikan untuk role berhak. PDF export di `api/routes/pdf_routes.py` membutuhkan auth. Logs memuat patient id, bukan PII full. | Demo public berisi data sintetik; aturan PHI tidak berlaku karena data bukan real. |
| D | Hapus seluruh pasien massal | Delete pasien membutuhkan role admin (`api/routes/patient_routes.py:209`); GCS object versioning fallback. | Tidak ada confirmation step UI untuk bulk delete; tidak relevan karena UI hanya delete satu per satu. |
| E | Masyarakat mengakses pasien orang lain | Ownership check eksplisit (`api/routes/patient_routes.py:157`) mengembalikan 403. | Tested via IDOR di Wave 1 audit. |

### 5.3 A3 openFDA API key

| STRIDE | Ancaman | Mitigasi nyata (file:line) | Residual |
|---|---|---|---|
| S | API key dipalsukan dari pihak ketiga | openFDA memvalidasi key di server mereka. Backend hanya mengirim sebagai `api_key` query param (`anggota1/openfda/fetch.py:272`). | None. |
| T | Diubah saat transit | TLS ke `api.fda.gov`. | None signifikan. |
| R | Tidak bisa membuktikan tim memang yang query | openFDA memberikan attribution per key; log line di backend mencatat panjang key tanpa nilai (`anggota1/openfda/fetch.py:503`). | Key tied ke akun Ghaisan saja. |
| I | Bocor di log, commit, atau output | Helper `_safe_params` mengganti `api_key` dengan `<redacted>` sebelum log (`anggota1/openfda/fetch.py:159`); `OPENFDA_API_KEY=` di-block oleh secret-scan hook (Section 8). | Operasional disiplin; tidak ada DLP otomatis. |
| D | Key dicabut oleh openFDA -> kuota 1000/hari | Skrip masih jalan tanpa key (kuota lebih rendah). | Performance hit; bukan blocker fungsionalitas. |
| E | Akses tanpa key namun di-attribute ke kami | openFDA bersifat publik; tidak ada elevation. | N/A. |

### 5.4 A4 User credentials (bcrypt hashes)

| STRIDE | Ancaman | Mitigasi nyata (file:line) | Residual |
|---|---|---|---|
| S | Login dengan password tebakan | bcrypt cost 12 (`api/auth.py:12`) memperlambat percobaan; error generik mencegah enumeration (A07). | **Tidak ada rate-limit / lockout** (R1). |
| T | Modifikasi hash di storage | Hash mutation tanpa kunci bcrypt menghasilkan login gagal. File JSON write membutuhkan akses fs/GCS (admin SA). | File JSON tidak atomic (lihat A08). |
| R | Tidak ada bukti login terjadi | Setiap login di-log dengan username dan hasil (`api/routes/auth_routes.py:27`/`:36`/`:39`). | Cloud Logging 30 hari default. |
| I | Hash bocor lewat response | `strip_password_fields` (`api/helpers.py:16`) dipanggil di list_users (`api/routes/admin_routes.py:45`) dan create_user (`api/routes/admin_routes.py:85`); login response tidak memuat hash (`api/routes/auth_routes.py:28`-`35`). | Tested di Wave 1. |
| D | Akun kunci dihapus -> tidak ada admin | Delete admin terakhir di-block: `api/routes/admin_routes.py:96`-`98`. | None. |
| E | Plaintext password masih ada di seed | Auto-hash on first read di `api/storage.py:90`-`98` me-replace `password_plain` dengan `password_hash`. | Seed JSON tetap memuat plaintext sampai server pertama kali jalan; mitigasi: file ada di `.gitignore` tidak relevan (seed memang di-commit untuk dev); demo credentials terbuka by design (lihat L1). |

### 5.5 A5 Scraped data openFDA

| STRIDE | Ancaman | Mitigasi nyata (file:line) | Residual |
|---|---|---|---|
| S | openFDA endpoint dipalsukan | TLS + DNS resolve langsung ke `api.fda.gov`. | Bergantung pada CA chain sistem. |
| T | Data dimanipulasi sebelum disimpan | Response JSON di-parse strict; tidak ada eksekusi konten. | None signifikan. |
| R | Tidak tahu kapan data terakhir refresh | Setiap pull menulis `_LAST_SCRAPE` dan log line (`api/routes/admin_routes.py:37`). | Tidak ada checksum file output. |
| I | Data publik sehingga disclosure low risk | Public data dari FDA. | N/A. |
| D | openFDA outage -> data tidak update | Polite delay + backoff (`anggota1/openfda/fetch.py:23` rule comment). 404 di-treat sebagai empty (rule 4 di docstring). | Demo tetap pakai cached snapshot. |
| E | Tidak ada elevation surface | N/A. | N/A. |

### 5.6 A6 Session token (cookie)

| STRIDE | Ancaman | Mitigasi nyata (file:line) | Residual |
|---|---|---|---|
| S | Cookie dicuri via XSS | `httpOnly: true` di `src/app/api/[...slug]/route.ts:82` mencegah `document.cookie` membaca. | XSS lain tidak otomatis steal token. |
| T | Mutasi cookie di browser | Cookie tetap memuat JWT yang ter-sign HMAC; mutasi menyebabkan verify fail. | None. |
| R | Tidak bisa membuktikan request berasal dari sesi tertentu | Setiap auth-required request di-log via middleware. | N/A. |
| I | Cookie dilihat di HTTP plain | `secure: process.env.NODE_ENV === "production"` (`src/app/api/[...slug]/route.ts:84`) memaksa HTTPS-only di prod. | Dev pakai Secure=false; risiko hanya di local network. |
| D | Cookie max-age habis -> user harus relogin | Max-age 12 jam menyeimbangkan UX dan security. | None. |
| E | CSRF state-changing route | SameSite=Lax (`src/app/api/[...slug]/route.ts:85`) + same-origin proxy. | Belum ada CSRF token eksplisit (R3). |

### 5.7 A7 Audit/operational logs

| STRIDE | Ancaman | Mitigasi nyata (file:line) | Residual |
|---|---|---|---|
| S | Log palsu di-inject ke stdout | Format Python logging fixed; tidak ada user-controlled newline yang ter-injection (Python logging escape default). | None signifikan. |
| T | Log dimodifikasi setelah ditulis | Cloud Logging append-only; user IAM tidak punya hak delete log entries. | Project owner bisa delete log sink (di luar threat model demo). |
| R | Repudiation aksi | Log line memuat username + path + role required (`api/middleware.py:44`-`47`). | Tidak ada signed log entries. |
| I | PII di log | Password tidak pernah di-log (verified). Patient ID di-log, full SOAP tidak. | Username sendiri bisa dianggap PII; akseptabel untuk demo. |
| D | Volume log diluar quota | Cloud Logging quota project free tier 50 GiB/bulan, demo well below. | None. |
| E | Akses log menambah privilege | Cloud Logging Viewer dibatasi project Owner saja. | None. |

---

## 6. Postur Keamanan Saat Pengiriman

Snapshot per 2026-05-18 (status implementasi mengikuti Wave 1 selesai + Wave 2 dokumentasi).

| Aset | Status | Last Verified | Notes |
|---|---|---|---|
| A1 JWT signing key | Tersimpan di Secret Manager (`medwatch-jwt-secret`); dev secret terpisah | 2026-05-04 (audit Wave 1) | Rotasi manual; lihat R4. |
| A2 Patient PII | RBAC backend aktif; data sintetik | 2026-05-04 | IDOR tested PASS. |
| A3 openFDA key | Env-only; secret-scan hook aktif | 2026-05-13 (run scraping real openFDA) | Tidak pernah ter-commit. |
| A4 bcrypt hashes | Cost 12; password_hash never returned | 2026-05-04 | A07 residual rate-limit. |
| A5 Scraped data | TLS ke api.fda.gov; polite delay | 2026-05-13 | Mitigasi DoS source di sisi FDA. |
| A6 Cookie token | httpOnly + Secure + SameSite=Lax | 2026-05-04 | CSRF token belum ada. |
| A7 Logs | INFO level, no PII full, no password | 2026-05-04 | 30-day retention default Cloud Logging. |

Ringkasan capaian terhadap acceptance keamanan mission:

- A01..A10 OWASP: 9 PASS, 1 PARTIAL (A04 karena CSRF token + rate-limit residual). Sumber: `docs/SECURITY_AUDIT.md` Section OWASP Top 10 Mapping.
- bcrypt cost 12, JWT issuer-validated, cookie httpOnly+Secure+SameSite, CORS allowlist eksplisit.
- Tidak ada nilai kredensial di repo (verified secret-scan; lihat Section 8).
- Service account JSON keys tidak pernah di-commit (gunakan default Cloud Run SA / Workload Identity di Vercel).

---

## 7. Batasan dan Hutang Keamanan (Residual Risk Register)

| ID | Risiko | Dampak | Likelihood | Mitigasi sementara | Owner | Rencana |
|---|---|---|---|---|---|---|
| R1 | Tidak ada rate-limit / account lockout pada `/api/auth/login` (`api/routes/auth_routes.py:13`) | Brute force credential mungkin (diperlambat oleh bcrypt) | Sedang | bcrypt cost 12, error generik, Cloud Run platform rate limit | Backend (Ghaisan) | Production: `flask-limiter` 5 attempts / 15 min / username. Lihat `ProductionGrade-ImplementationPlan/04-hardening-plan.md`. |
| R2 | Audit trail minimal: admin actions hanya di stdout (Cloud Logging 30 hari) | Forensik insiden sulit setelah 30 hari | Rendah | Cloud Logging Cloud Run otomatis; log line memuat aktor | Backend | Production: durable audit log di Cloud Storage + retention 1 tahun. |
| R3 | Tidak ada CSRF token untuk state-changing route | CSRF attack via same-origin theoretical | Rendah | SameSite=Lax cookie + same-origin proxy Vercel | Frontend | Production: double-submit cookie atau header `X-Requested-With` validation. |
| R4 | Rotasi JWT secret manual | Compromise kunci akan mempengaruhi seluruh token aktif sampai expiry 12 jam | Rendah | Secret di Secret Manager; bukan inline kode | Sysadmin | Production: rotasi quarterly via Secret Manager versions + dual-key window. |
| R5 | Dependency scanning belum di CI | CVE baru hanya terdeteksi saat audit manual | Rendah | `pip-audit` + `npm audit` jalan saat security-analyst agent | DevOps | Tambah GitHub Actions `pip-audit` + `npm audit --omit=dev` per PR. |
| R6 | Penulisan JSON tidak atomic (`api/storage.py:38`) | Crash di tengah write -> file korup | Rendah | GCS object versioning untuk recovery | Backend | Implementasi `write-to-temp + os.replace` pattern. |
| R7 | Direct backend Cloud Run `--allow-unauthenticated` | Bypass proxy memungkinkan secara teknis | Rendah | Backend RBAC tetap menolak token absen/invalid (defense in depth) | Sysadmin | Production: Cloud Run IAM `roles/run.invoker` hanya untuk Vercel IP range atau private VPC peering. |
| R8 | Frontend high-severity deps di `_archived/` paths (H5, H6) | Tidak runtime; risiko jika archived route di-restore | Rendah | Tidak ada route aktif yang me-load paket bermasalah | Frontend | `npm uninstall react-simple-maps react-force-graph-2d ...` setelah konfirmasi pages tidak di-restore. |

---

## 8. Praktik Operasional

Section ini menjabarkan disiplin operasional yang dipertahankan tim selama mission, sesuai mission constraint 7 (Indonesian context + dokumentasi formal), 10 (no destructive git/push), dan 12 (credential anti-leak).

### 8.1 Per-commit secret scan (mission constraint 12)

Setiap commit di-block oleh script `./scripts/secret-scan.sh` jika staged diff memuat pola berbahaya:

- `sk-...` (OpenAI /  API key)
- `ghp_`, `gho_` (GitHub PAT)
- `AKIA[0-9A-Z]{16}` (AWS access key id)
- `xox[abprs]-` (Slack token)
- `BEGIN .* PRIVATE KEY` (PEM private key)
- `JWT_SECRET=<non-placeholder value>`
- `api_key=<non-placeholder value>`
- Inline service-account JSON
- Connection string `://user:password@`

Pada match, commit di-abort, finding di-record sebagai `open_blocker`, dan diff di-redact sebelum commit ulang.

### 8.2 Service account key files tidak di repo

- Cloud Run menggunakan default service account `517694123086-compute@developer.gserviceaccount.com` (resource name OK; lihat `docs/SECURITY_AUDIT.md` GCP IAM Review). Tidak ada `service-account.json` di-download untuk lokal.
- Vercel menggunakan OIDC Workload Identity Federation atau Vercel-managed env var; tidak ada GCP SA key di-export ke `.env.local`.
- `.gitignore` backend (`.gitignore:18`-`28`) dan frontend (`FrontendMedWatch/.gitignore:25`, `:34`) mengecualikan `*.pem`, `*.key`, `service-account*.json`, `gcp-key*.json`, `.env.local`.

### 8.3 Verifikasi .gitignore (deliverable W2-D10)

Saat dokumen ini ditulis, `.gitignore` backend memuat (line numbers per state Wave 2):

```
.env
.env.*
.env.local
!.env.example
*.pem
*.key
service-account*.json
gcp-key*.json
```

`.gitignore` frontend memuat `.env*`, `*.pem`, `.env*.local`. Kombinasi ini mencegah commit value secret yang umum. `.env.example` (template tanpa nilai) sengaja tidak di-ignore agar developer baru tahu env apa yang dibutuhkan.

### 8.4 Aturan emergency rotasi (constraint 10)

Jika real secret terdeteksi di history git:

1. Mark file sebagai compromised di `.mission/findings/security/`.
2. **Rotate dahulu** (Cloud Console: Secret Manager `Add new version`; openFDA: re-issue key).
3. Update Cloud Run revision / `.env.local` developer dengan versi baru.
4. **Tidak melakukan** `git filter-branch`, `bfg`, atau `git push --force`; history rewriting di-block oleh mission constraint 10 untuk repo academic. Catat di `.mission/blockers/` jika dosen meminta history clean.

### 8.5 Akun terlarang

Akun `dudungdotnet@gmail.com` tidak boleh dilibatkan di operasi GCP/Vercel manapun (mission constraint). Verifikasi rutin: `gcloud projects get-iam-policy medwatch-polban-2026 --format=json | grep dudungdotnet` harus tidak ada hasil.

---

## 9. Daftar Periksa Sebelum Demo

Sebelum sesi presentasi di hadapan dosen pendamping (Aprianti Nanda Sari, Ade Chandra Nugraha, Ardhian Ekawijana) pada 25 Mei 2026 atau jadwal kelas berikutnya, jalankan checklist berikut:

### 9.1 Backend (Cloud Run)

- [ ] `gcloud run services describe medwatch-api --region asia-southeast1 --format='value(status.url)'` mengembalikan URL aktif.
- [ ] `curl <url>/health` mengembalikan 200 OK.
- [ ] `curl -X POST <url>/api/auth/login -H 'Content-Type: application/json' -d '{"username":"admin_demo","password":"<dummy>"}'` mengembalikan 401 (kredensial demo nyata diuji secara manual, bukan di-commit ke checklist ini).
- [ ] `FLASK_DEBUG` env Cloud Run revision aktif bernilai `false` (`gcloud run services describe ... | grep DEBUG`).
- [ ] Secret Manager `medwatch-jwt-secret` memiliki minimal satu enabled version.
- [ ] IAM bucket `medwatch-polban-2026-state` tidak memuat binding `allUsers` atau `allAuthenticatedUsers`: `gsutil iam get gs://medwatch-polban-2026-state`.

### 9.2 Frontend (Vercel)

- [ ] `medwatch-frontend.vercel.app` me-load `/login` tanpa error console.
- [ ] Env `BACKEND_API_URL` di Vercel project settings ter-set ke Cloud Run URL (verifikasi via `vercel env ls`, jangan print value).
- [ ] `NEXT_PUBLIC_*` env tidak memuat nilai sensitif (verifikasi via `vercel env ls`).
- [ ] Cookie `medwatch_token` setelah login memiliki flag HttpOnly + Secure + SameSite=Lax (DevTools Application -> Cookies).

### 9.3 Repository hygiene

- [ ] `git log --all --oneline | wc -l` masuk akal (no force-push history rewrite).
- [ ] `grep -rE "JWT_SECRET=.{20,}" .` (excluding `.env.example`) tidak menghasilkan match.
- [ ] `grep -rE "OPENFDA_API_KEY=.{10,}" .` (excluding `.env.example`) tidak menghasilkan match.
- [ ] `find . -name 'service-account*.json' -o -name 'gcp-key*.json'` tidak menghasilkan match.
- [ ] `git status --ignored | grep -E "\.env|\.pem"` mengkonfirmasi file sensitif lokal masuk gitignore (bukan tracked).

### 9.4 Dokumen demo

- [ ] `docs/SECURITY.md` (file ini) ter-commit dan terbaca.
- [ ] `docs/SECURITY_AUDIT.md` tersinkron dengan kondisi terbaru.
- [ ] `README.md` baru (W2-D12) merujuk dokumen keamanan ini.
- [ ] `ProductionGrade-ImplementationPlan/04-hardening-plan.md` menjabarkan R1..R8 dengan rencana konkret.

### 9.5 Skenario QA singkat (untuk Bimo)

| Skenario | Ekspektasi |
|---|---|
| Login dengan password salah 3x | Semua 3 attempts mengembalikan 401; tidak ada lockout (R1) |
| User masyarakat akses `/admin/dashboard` | Redirect ke `/drug-search` (frontend) ATAU 403 (backend direct) |
| User masyarakat GET `/api/patients/P001` orang lain | 403 |
| Login tanpa JWT akses `/api/patients` | 401 |
| Cookie `medwatch_token` di-paste di tab incognito beda browser | Login tetap valid sampai expiry 12 jam (stateless JWT) |
| Logout lalu re-akses dashboard | Redirect ke `/login` (cookie cleared) |

---

## 10. Lampiran: Referensi Standar

- OWASP Top 10:2021 -> https://owasp.org/Top10/
- OWASP Password Storage Cheat Sheet -> https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- Microsoft STRIDE -> https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats
- NIST SP 800-63B Section 5.1.1.2 (Memorized Secret Verifiers) untuk pedoman bcrypt cost.
- OWASP ASVS v4.0.3 -> https://owasp.org/www-project-application-security-verification-standard/ (informational benchmark)
- IEEE/ISO/IEC 27001:2022 -> referensi tata kelola; tidak diadopsi penuh untuk demo akademik tetapi prinsip control objective dipakai.

---

## Lampiran A: File yang dirujuk

| Path | Tujuan kutipan |
|---|---|
| `api/auth.py` | bcrypt + JWT primitives |
| `api/middleware.py` | `@require_auth`, `@require_role` |
| `api/config.py` | env reading (JWT_SECRET, OPENFDA_API_KEY, CORS allowlist) |
| `api/storage.py` | JSON storage + auto-hash plaintext password seed |
| `api/helpers.py` | `strip_password_fields` + helper response |
| `api/app.py` | Flask app init, CORS, error handlers, header strip |
| `api/routes/auth_routes.py` | Login + me + logout |
| `api/routes/admin_routes.py` | Admin scrape, user CRUD, system stats |
| `api/routes/patient_routes.py` | Patient CRUD + RBAC + range validation |
| `api/routes/safety_routes.py` | Drug safety check (require_auth) |
| `api/routes/drug_routes.py` | Drug catalog (public list) |
| `anggota1/openfda/fetch.py` | openFDA pull (api_key handling, polite delay) |
| `src/proxy.ts` | Edge middleware: public/admin routing + role decode |
| `src/app/api/[...slug]/route.ts` | Catch-all proxy Vercel -> Cloud Run + cookie set/clear |
| `.gitignore` (backend) | Excludes `.env*`, `*.pem`, service-account JSON, dst |
| `FrontendMedWatch/.gitignore` | Excludes `.env*`, `*.pem`, `.vercel` |
| `docs/SECURITY_AUDIT.md` | Hands-on audit Wave 1 (sumber komplementer) |

---

Dokumen ini ditulis untuk Proyek 1 Pengembangan Perangkat Lunak Desktop, Politeknik Negeri Bandung, Semester 2 TA 2025/2026 oleh Kelompok B5. Versi 1.0 dirilis 2026-05-18 oleh Ghaisan Khoirul Badruzaman (NIM 251524048).
