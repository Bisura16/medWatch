---
title: Production Hardening Plan MedWatch
version: 1.0
owner: Ghaisan Khoirul Badruzaman (NIM 251524048, Project Leader Kelompok B5)
date: 2026-05-18
status: forward-looking plan (belum diimplementasi)
references:
  - OWASP Top 10:2021 (owasp.org/Top10/)
  - OWASP ASVS v4.0.3
  - NIST SP 800-63B
related_docs:
  - docs/SECURITY.md
  - docs/SECURITY_AUDIT.md
  - ProductionGrade-ImplementationPlan/00-overview.md
  - ProductionGrade-ImplementationPlan/02-offline-implementation-plan.md
  - ProductionGrade-ImplementationPlan/06-roadmap.md
---

# 04 - Production Hardening Plan MedWatch

Dokumen ini menjabarkan rencana hardening yang menutup Residual Risk Register R1-R8 yang sudah didokumentasikan di `docs/SECURITY.md` Section 7. Setiap residual risk dipasangkan dengan rencana konkret implementasi, vendor library/pattern yang dipilih, dan acceptance criteria. Hardening dijalankan pada Phase 3 di `06-roadmap.md` (Agustus 2026), setelah Phase 2 packaging selesai.

---

## 1. Konteks dan Ruang Lingkup

### 1.1 Cakupan hardening

Dokumen `docs/SECURITY.md` (Wave 2 W2-D10) mendokumentasikan postur keamanan AS-BUILT pada 18 Mei 2026 termasuk 8 residual risk (R1-R8). Hardening plan ini mengubah 8 residual risk tersebut dari status "open" menjadi "mitigated" dengan implementasi nyata. Cakupan teknis: backend Flask di `api/`, persistensi data, logging, dan dependency management.

### 1.2 Out of scope hardening v1.0

- Cloud-only hardening (Cloud Run private VPC, IAP). MedWatch production offline-first, Cloud Run hanya untuk demo akademik.
- Pen-test eksternal oleh vendor security. Out of budget per mission constraint 6.
- Sertifikasi SOC 2 / ISO 27001. Tidak relevan untuk single-Faskes deployment.
- Compliance HIPAA / UU PDP. Software ini memproses data demo, bukan PHI nyata; produksi nyata di Faskes 1 di Indonesia tetap memerlukan compliance dengan UU 27/2022 PDP namun di-defer sampai ada klien yang membayar.

### 1.3 Standar yang dipakai

- OWASP Top 10:2021 sebagai checklist utama.
- OWASP ASVS v4.0.3 level 1 sebagai benchmark target.
- NIST SP 800-63B untuk pedoman password storage (sudah diadopsi: bcrypt cost 12, lihat `api/auth.py:12`).

---

## 2. Mapping Residual Risk -> Hardening Item

Setiap R1-R8 dipetakan ke satu atau lebih hardening item. Numbering hardening item (H1, H2, ...) tidak harus 1:1 dengan R.

| Residual Risk | Hardening Item |
|---|---|
| R1 No rate limit pada login | H1 flask-limiter integration |
| R2 Audit trail minimal | H2 structured JSON logs + durable audit table |
| R3 No CSRF token | H3 double-submit cookie pattern |
| R4 JWT secret rotation manual | H4 dual-key rotation procedure |
| R5 No CI dependency scanning | H5 GitHub Actions pip-audit + npm audit |
| R6 Non-atomic JSON writes | H6 SQLite migration (sudah dibahas di 02-offline) atau atomic-rename pattern |
| R7 Cloud Run --allow-unauthenticated | H7 Cloud Run IAM lockdown (jika cloud demo terus berjalan) |
| R8 Frontend archived deps high-severity | H8 cleanup archived routes |

---

## 3. H1: Rate Limit pada `/api/auth/login`

### 3.1 Status saat ini

Per `docs/SECURITY.md` Section 7 Item R1 dan A07 baris 168: `api/routes/auth_routes.py:13` `POST /api/auth/login` tidak memiliki rate limit. bcrypt cost 12 (`api/auth.py:12`) memperlambat throughput brute force, namun secara teoretis attacker dengan sabar dapat melakukan credential stuffing.

### 3.2 Rencana implementasi

Library pilihan: [flask-limiter](https://flask-limiter.readthedocs.io/) versi 3.x. Bebas, aktif maintained, mendukung in-memory backend untuk single-process deployment.

Pseudocode integrasi:

```python
# api/app.py addition
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="memory://",
    default_limits=[],
)

# api/routes/auth_routes.py modification (dekorator tambahan)
@bp.route("/login", methods=["POST"])
@limiter.limit("5 per 15 minutes", key_func=lambda: request.json.get("username", "anon"))
def login():
    ...
```

Catatan: key_func di-override untuk per-username throttling, bukan per-IP, agar ribuan IP berbeda tidak bisa brute force satu akun. Trade-off: legitimate user yang typo password 6 kali dalam 15 menit akan terkunci (false positive).

### 3.3 Acceptance

- `curl -X POST /api/auth/login` dengan password salah 5 kali berturut-turut dalam 15 menit: ke-6 request mendapat HTTP 429.
- Pesan response: `{"error": "Terlalu banyak percobaan login. Silakan coba lagi dalam 15 menit."}`.
- Log line di stdout: `WARNING auth_routes: rate limit hit for username=<x>`.
- Setelah 15 menit, request berikutnya kembali diterima normal.

### 3.4 Hardware/operational considerations

Karena MedWatch production single-Faskes deployment, attacker eksternal hampir tidak ada (network internal Faskes). H1 lebih sebagai pertahanan jika seseorang di klinik mencoba menebak password kolega. In-memory storage flask-limiter cukup; tidak butuh Redis.

---

## 4. H2: Structured JSON Logs + Durable Audit Trail

### 4.1 Status saat ini

Per `docs/SECURITY.md` Section 7 Item R2: logging dilakukan via stdlib Python `logging` (`api/app.py:20`) dengan format text. Cloud Logging retain 30 hari default.

Untuk production offline, Cloud Logging tidak relevan. Yang dibutuhkan: file log lokal yang structured (JSON line) agar mudah di-parse jika klien mengirimkan via support channel.

### 4.2 Rencana implementasi

Library: [python-json-logger](https://github.com/madzak/python-json-logger) untuk format JSON line.

Modifikasi `api/app.py`:

```python
import logging
from pythonjsonlogger import jsonlogger

log_handler = logging.FileHandler(
    os.path.join(DATA_DIR, "logs", "audit.log"),
    encoding="utf-8",
)
formatter = jsonlogger.JsonFormatter(
    "%(asctime)s %(levelname)s %(name)s %(message)s %(actor)s %(action)s %(resource)s"
)
log_handler.setFormatter(formatter)
logging.getLogger().addHandler(log_handler)
```

Format JSON line memungkinkan analisis sederhana dengan `jq`:

```bash
cat audit.log | jq 'select(.action=="login" and .levelname=="ERROR")'
```

### 4.3 PII Redaction

Hardening rule penting: log tidak boleh mengandung password atau JWT token apa adanya. Verifikasi:

- `api/routes/auth_routes.py:27`, `:36`, `:39` saat ini log username, bukan password. Sudah OK.
- Path log: `<appdata>/logs/audit.log` (Windows). Rotation: harian, retain 30 hari, lalu auto-delete via `logging.handlers.TimedRotatingFileHandler`.

### 4.4 Durable audit table di SQLite

Untuk action-action sensitive (login, user create, scrape trigger), tulis dual: ke stdout DAN ke tabel `audit_log` di SQLite:

```sql
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    actor TEXT,
    action TEXT NOT NULL,
    resource TEXT,
    result TEXT,
    ip TEXT
);
```

Wrapper helper `api/audit.py` (akan dibuat):

```python
def audit(actor: str, action: str, resource: str = "", result: str = "success", ip: str = ""):
    conn = get_db()
    conn.execute(
        "INSERT INTO audit_log (timestamp, actor, action, resource, result, ip) VALUES (?, ?, ?, ?, ?, ?)",
        (datetime.utcnow().isoformat(), actor, action, resource, result, ip),
    )
    conn.commit()
    logger.info("audit", extra={"actor": actor, "action": action, "resource": resource, "result": result})
```

### 4.5 Acceptance

- Log file `audit.log` ada di `<appdata>/logs/` setelah aplikasi berjalan minimal 1 hari.
- Setiap login berhasil/gagal muncul sebagai 1 line JSON dengan field `action`, `actor`, `result`.
- Query SQLite `SELECT * FROM audit_log WHERE action='login_failed' ORDER BY timestamp DESC LIMIT 10` mengembalikan minimal 10 entries setelah test.
- Password values tidak pernah muncul di log file (verifikasi grep).

---

## 5. H3: CSRF Token (Double-Submit Cookie)

### 5.1 Status saat ini

Per `docs/SECURITY.md` Section 7 Item R3 dan A04 baris 136: tidak ada CSRF token eksplisit. Mitigasi yang sudah berjalan: cookie SameSite=Lax (`src/app/api/[...slug]/route.ts:85`) + same-origin proxy.

Untuk MedWatch desktop offline, CSRF kurang relevan karena tidak ada browser yang mengakses backend dari origin lain. Namun jika versi production tetap memiliki layer web showcase (sebagai demo opsional), CSRF protection tetap berguna.

### 5.2 Rencana implementasi

Pattern: [double-submit cookie](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html#double-submit-cookie). Backend issue cookie `csrf_token` saat login. Frontend membaca cookie tersebut dan mengirimkan nilai yang sama di header `X-CSRF-Token` pada setiap state-changing request.

Library opsional: [flask-wtf](https://flask-wtf.readthedocs.io/) menyediakan CSRFProtect, namun karena MedWatch tidak pakai forms tradisional, implementasi manual lebih bersih.

### 5.3 Acceptance

- Login response menyertakan Set-Cookie: csrf_token=<random_32_byte_hex>; SameSite=Lax (BUKAN HttpOnly, karena harus dapat dibaca oleh JavaScript frontend).
- POST/PUT/DELETE request tanpa header `X-CSRF-Token` ditolak 403.
- POST/PUT/DELETE request dengan `X-CSRF-Token` yang tidak match cookie ditolak 403.

### 5.4 Prioritas

Karena MedWatch production primarily desktop offline, H3 dapat dijadwalkan setelah H1 dan H2 selesai. Jika layer web demo dibutuhkan untuk presentasi tambahan, H3 dieksekusi lebih cepat.

---

## 6. H4: JWT Secret Rotation Procedure

### 6.1 Status saat ini

Per `docs/SECURITY.md` Section 7 Item R4: JWT secret tersimpan di Secret Manager (Cloud Run demo) atau env var lokal. Rotasi belum otomatis; bila kunci compromise, semua token aktif sampai expiry 12 jam.

### 6.2 Rencana implementasi (desktop production)

Untuk MedWatch desktop offline, JWT secret di-generate di first run dan disimpan di `<appdata>/.jwt-key` dengan permission 600 (lihat `02-offline-implementation-plan.md` Section 7). Rotasi:

Prosedur dual-key window (jika compromise diketahui):

1. Aplikasi menerima dua secret: `current` dan `previous`.
2. Token baru di-sign dengan `current`.
3. Saat verify: coba `current` dulu, kemudian `previous`. Berhasil di salah satu = valid.
4. Setelah 24 jam, `previous` di-delete dari config. Semua token yang di-sign dengan `previous` otomatis invalid.

File `<appdata>/jwt-keys.json`:

```json
{
  "current": {"id": "k2", "secret_hex": "<redacted>", "created": "2026-08-15"},
  "previous": {"id": "k1", "secret_hex": "<redacted>", "created": "2026-06-01"}
}
```

Implementasi di `api/auth.py:30-40`:

- Saat sign: gunakan `current.secret_hex`, embed `kid: current.id` di header JWT.
- Saat verify: baca `kid` dari header, lookup secret di `current` atau `previous`.

### 6.3 Acceptance

- Saat user klik menu Admin -> "Rotasi Kunci JWT", aplikasi mempromosikan `current` ke `previous`, generate `current` baru.
- Token yang di-sign sebelum rotasi tetap valid sampai 24 jam.
- Setelah 24 jam, token lama otomatis ditolak (verify gagal).

### 6.4 Catatan operasional

Untuk single-Faskes, kemungkinan compromise rendah (tidak ada attacker yang punya akses ke `<appdata>/.jwt-key` kecuali sudah punya akses ke OS user). H4 lebih sebagai disiplin best practice.

---

## 7. H5: CI Dependency Scanning

### 7.1 Status saat ini

Per `docs/SECURITY.md` Section 7 Item R5: `pip-audit` dan `npm audit` dijalankan manual saat security-analyst agent run. Tidak ada CI yang menjalankan otomatis per PR.

### 7.2 Rencana implementasi

File baru: `.github/workflows/security-scan.yml`. Workflow trigger: push ke `main`, pull request, dan jadwal weekly (cron `0 8 * * 1`).

Outline workflow:

```yaml
name: Security Scan
on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: '0 8 * * 1'  # Setiap Senin pagi WIB

jobs:
  pip-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      - run: pip install pip-audit
      - run: pip-audit -r api/requirements.txt --strict
  npm-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          repository: Finerium/FrontendMedwatch
          path: frontend
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - run: cd frontend && npm ci
      - run: cd frontend && npm audit --omit=dev --audit-level=high
```

Pada match high/critical vulnerability, workflow gagal dan menjadi blocking untuk merge.

### 7.3 Acceptance

- Workflow `security-scan.yml` ter-trigger pada PR baru.
- Status check muncul di GitHub PR UI.
- High/critical vulnerability mem-block merge.
- Weekly cron run berjalan tanpa intervensi manual.

---

## 8. H6: SQLite Migration (atau Atomic Rename Pattern)

### 8.1 Status saat ini

Per `docs/SECURITY.md` Section 7 Item R6: `api/storage.py:38` membuka file mode `w` dengan `json.dump`. Tidak atomic.

### 8.2 Rencana implementasi

Sudah dibahas mendalam di `02-offline-implementation-plan.md` Section 4. Dua opsi:

- **Pilihan utama**: migrasi ke SQLite. Lebih banyak benefit (atomicity, indexing, transactional updates).
- **Bridging strategy**: jika SQLite migration terlalu besar untuk v1.0, terapkan atomic-rename pattern:
  ```python
  def _save_local_atomic(filename: str, data: Any) -> None:
      path = DATA_DIR / filename
      tmp = path.with_suffix(path.suffix + ".tmp")
      with open(tmp, "w", encoding="utf-8") as f:
          json.dump(data, f, indent=2, ensure_ascii=False)
      os.replace(tmp, path)  # atomic on POSIX dan Windows
  ```

### 8.3 Acceptance

- Tes: kill -9 aplikasi saat sedang `_save_local`. Setelah restart, file `patients.json` tetap valid JSON (baik versi sebelum maupun sesudah save, tetapi tidak corrupt).
- Test integrasi: 1000 save berturut-turut tidak menghasilkan file corrupt (run dengan random kill probability 5%).

---

## 9. H7: Cloud Run IAM Lockdown (jika demo terus jalan)

### 9.1 Status saat ini

Per `docs/SECURITY.md` Section 7 Item R7: Cloud Run service `medwatch-api` dikonfigurasi `--allow-unauthenticated`. Mitigasi backend RBAC tetap berlaku tetapi bypass proxy frontend secara teknis mungkin.

### 9.2 Rencana implementasi

Untuk demo akademik tetap, ini OK karena dosen pendamping perlu akses langsung untuk verifikasi. Untuk production-grade, hardening:

- Cloud Run IAM binding hanya untuk specific Vercel service account atau range IP Vercel edge (jika tersedia daftar IP publik Vercel).
- Alternatif: pakai Cloud Run authentication dengan service account dari Vercel via OIDC token, sehingga Vercel edge perlu sign request sebelum forward ke Cloud Run.

### 9.3 Catatan relevansi

H7 hanya relevan jika layer web demo dipertahankan setelah submission akademik. Untuk production desktop offline, H7 tidak applicable. Jika tim memutuskan men-decommission Cloud Run setelah submission, H7 di-skip dan ditandai N/A.

---

## 10. H8: Cleanup Frontend Archived Routes

### 10.1 Status saat ini

Per `docs/SECURITY.md` Section 7 Item R8: frontend memiliki dependency high-severity di route archived (H5, H6, H7 di `docs/SECURITY_AUDIT.md`).

### 10.2 Rencana implementasi

Jika layer web demo akademik dipertahankan, hardening:

- `npm uninstall react-simple-maps react-force-graph-2d` dan paket lain di archived paths.
- Konfirmasi route `_archived/` tidak akan di-restore (delete folder).
- Re-run `npm audit` -> high severity hilang.

### 10.3 Acceptance

- `npm audit --omit=dev --audit-level=high` mengembalikan 0 vulnerabilities.
- Bundle size frontend turun (positive side effect).

---

## 11. Tambahan: Hardening Lain di Luar Residual Risk

### 11.1 Input Validation Hardening dengan Pydantic

Saat ini `api/routes/patient_routes.py:56` `_validate_medical_ranges` melakukan validasi manual. Untuk production, gunakan library schema validation seperti [pydantic](https://docs.pydantic.dev/) atau [marshmallow](https://marshmallow.readthedocs.io/) untuk konsistensi.

Outline pydantic schema:

```python
from pydantic import BaseModel, Field, validator

class PatientSOAP(BaseModel):
    id: str = Field(pattern=r"^P\d{3}$")
    nama: str = Field(min_length=1, max_length=100)
    umur: int = Field(ge=0, le=130)
    tanggal_kunjungan: str = Field(pattern=r"^\d{2}-\d{2}-\d{4}$")
    # ... rest of canonical SOAP schema per .md line 95-105
```

Benefit: error messages otomatis, schema documentation auto-generated, type-safe.

### 11.2 User-Friendly Indonesian Error Messages

Pengganti generic `"internal server error"` di `api/app.py:53`. Implementasi:

```python
ERROR_MESSAGES_ID = {
    "auth_required": "Anda perlu login terlebih dahulu.",
    "role_denied":   "Anda tidak memiliki hak akses untuk fitur ini.",
    "not_found":     "Data yang dicari tidak ditemukan.",
    "validation":    "Ada kesalahan pada data yang dimasukkan. Periksa kembali.",
    "internal":      "Terjadi kesalahan internal. Silakan hubungi tim support.",
}
```

Stack trace tidak pernah tampil ke user; hanya dicatat di `audit.log`.

### 11.3 Pre-Generated Visualization Cache

Saat ini visualisasi `anggota3/TampilGrafik.py` dijalankan setiap kali halaman dashboard dibuka. Untuk first-run UX yang instan, generate PNG saat install/build (build-time) dan cache di `<appdata>/cache/`. Refresh otomatis saat data baru di-CRUD (invalidation hook).

### 11.4 Dependency Pinning (sudah di-implement di MVP)

`api/requirements.txt` sudah memakai pin `==`. Production tetap pakai pattern yang sama. Update versi dilakukan via PR yang men-trigger H5 CI scan.

---

## 12. OWASP Top 10 Posture Setelah Hardening

Target setelah H1-H8 selesai (per `docs/SECURITY.md` Section 6 awal: 9 PASS, 1 PARTIAL):

| Kategori | Sebelum | Setelah |
|---|---|---|
| A01 Broken Access Control | PASS | PASS |
| A02 Cryptographic Failures | PASS | PASS |
| A03 Injection | PASS | PASS (+ pydantic schema) |
| A04 Insecure Design | PARTIAL (R3) | PASS (H3) |
| A05 Security Misconfiguration | PASS | PASS |
| A06 Vulnerable Components | PASS | PASS (+ H5 CI auto) |
| A07 Auth Failures | PARTIAL (R1) | PASS (H1) |
| A08 Data Integrity | PARTIAL (R6) | PASS (H6) |
| A09 Logging Failures | PARTIAL (R2) | PASS (H2) |
| A10 SSRF | PASS | PASS |

Target: **10/10 PASS** untuk versi 1.0 production.

---

## 13. Tanggung Jawab dan Estimasi Waktu

| Hardening | PIC saran | Estimasi |
|---|---|---|
| H1 flask-limiter | Ghaisan | 0.5 hari |
| H2 structured JSON logs + audit table | Ghaisan | 1 hari |
| H3 CSRF token (jika web demo dipertahankan) | Ghaisan | 1 hari |
| H4 JWT rotation procedure | Ghaisan | 0.5 hari |
| H5 CI dependency scanning | Ghaisan | 0.5 hari |
| H6 SQLite migration (sudah di 02-offline) | Ghaisan | Tercakup di 02-offline |
| H7 Cloud Run IAM lockdown (jika demo on) | Ghaisan | 0.5 hari |
| H8 cleanup archived deps | Ghaisan | 0.5 hari |
| Pydantic schema migration | Ghaisan | 1 hari |
| Indonesian error messages | Abhidal (UI/UX) | 0.5 hari |
| Pre-generated viz cache | Alia | 1 hari |
| Test security regressions | Bimo (QA) | 2 hari |
| Total | | 9 hari kerja |

Pekerjaan dijadwalkan di Phase 3 di `06-roadmap.md` (Agustus 2026).

---

## 14. Tanggal dan Pemilik

- Tanggal dokumen: 18 Mei 2026.
- Pemilik: Ghaisan Khoirul Badruzaman (NIM 251524048).
- Status: forward-looking plan. Eksekusi dijadwalkan di Phase 3 (Agustus 2026).
