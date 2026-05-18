# MEDWATCH

## INOVASI SISTEM INFORMASI KESEHATAN BERBASIS DESKTOP UNTUK MONITORING KEAMANAN OBAT DAN MANAJEMEN PASIEN PADA FASKES TINGKAT PERTAMA

| No | Nama                         | NIM       | GitHub           |
|----|------------------------------|-----------|------------------|
| 1  | Bimo Surya Anggara           | 251524040 | Bisura16         |
| 2  | Ghaisan Khoirul Badruzaman   | 251524048 | Ghaisank         |
| 3  | Abhidal Muhammad Gazza       | 251524032 | AbhidalMG        |
| 4  | Muhammad Iqbal               | 251524057 | Ballvoldigoad    |
| 5  | Alia Ardani                  | 251524035 | vssixla          |

## APLIKASI MEDWATCH
MedWatch merupakan aplikasi sistem informasi kesehatan berbasis desktop yang dirancang untuk membantu fasilitas kesehatan tingkat pertama (Faskes 1) dalam mengelola data pasien serta melakukan monitoring keamanan obat. Aplikasi ini mengintegrasikan fitur rekam medis digital, pengecekan keamanan obat, visualisasi data kesehatan, dan ekspor laporan dalam satu platform berbasis Python dengan konsep offline-first. 

MedWatch memanfaatkan web scraping dari sumber farmasi terpercaya untuk menyediakan informasi efek samping, recall obat, dan peringatan keamanan obat sehingga dapat membantu tenaga kesehatan maupun masyarakat dalam memperoleh informasi kesehatan yang lebih cepat, terstruktur, dan mudah diakses.

## SISTEM UNTUK MENJALANKAN APLIKASI
- **Python**, digunakan sebagai bahasa pemrograman utama untuk membangun dan menjalankan seluruh fungsi aplikasi.
- **CustomTkinter**, digunakan untuk membuat antarmuka grafis (GUI) modern sehingga pengguna dapat berinteraksi dengan aplikasi dengan tampilan yang lebih interaktif.
- **Requests**, digunakan untuk mengambil data halaman web melalui HTTP request dalam proses web scraping.
- **BeautifulSoup4**, digunakan untuk memproses dan mengekstrak informasi dari struktur HTML halaman web.
- **Matplotlib**, digunakan untuk membuat visualisasi data kesehatan seperti grafik tren kunjungan pasien dan distribusi keluhan.
- **FPDF2**, digunakan untuk membuat dan mengekspor laporan dalam format PDF.
- **Pillow**, digunakan untuk pengolahan gambar seperti ikon dan elemen antarmuka aplikasi.
- **JSON Module**, digunakan untuk membaca dan menyimpan data lokal dalam format JSON. Modul ini merupakan modul bawaan Python sehingga tidak memerlukan instalasi tambahan.
- **OS dan Datetime Module**, digunakan untuk pengelolaan file sistem dan pengolahan tanggal/waktu pada aplikasi. Modul ini juga merupakan modul bawaan Python.


## Integration Layer: `api/` (added by Ghaisan, branch `ghaisan-APIIntegration`)

> Section ini ditambahkan oleh Ghaisan Khoirul Badruzaman di branch `ghaisan-APIIntegration`. Modul anggota1-5 tidak diubah. Section di atas garis ini tetap milik Bimo (asli).

Folder `api/` di root repo ini adalah integration layer Flask yang membungkus modul anggota1-5 menjadi REST endpoints, dideploy ke GCP Cloud Run, dan dikoneksikan ke frontend Next.js di Vercel.

- **API code:** [`./api/`](./api/)
- **API documentation:** [`./api/README.md`](./api/README.md)
- **Architecture diagrams:** [`./docs/diagrams/`](./docs/diagrams/) (18 diagrams: drawio source + PNG)
- **Integration guide:** [`./docs/INTEGRATION_GUIDE.md`](./docs/INTEGRATION_GUIDE.md)
- **Scope note for lecturer:** [`./docs/SCOPE_NOTE.md`](./docs/SCOPE_NOTE.md)
- **Security audit:** [`./docs/SECURITY_AUDIT.md`](./docs/SECURITY_AUDIT.md)
- **Live backend:** https://medwatch-api-517694123086.asia-southeast1.run.app
- **Live frontend:** https://medwatch-frontend.vercel.app

## Merge layer: `integrasi/`

Folder `integrasi/` adalah desktop CLI app yang nge-compose anggota1-5 jadi satu entry point dengan role-based menu. Implementasi target tim "merge masing-masing modul" tanpa modify file anggota satu pun.

```bash
python integrasi/app_terpadu.py
# Login: admin1 / admin123  (admin)
# Login: bidan1 / bidan123  (tenaga_kesehatan)
```

Lihat [`./integrasi/README.md`](./integrasi/README.md) untuk detail.

## Quick start backend (web layer)

```bash
cd api
pip install -r requirements.txt
JWT_SECRET=dev-only python -m flask --app api.app run --port 8080
# visit http://localhost:8080/ for endpoint docs
```

Lihat [`./api/README.md`](./api/README.md) untuk endpoint reference, demo credentials, dan deployment commands.

---

## Sumber Data dan Teknis Scraping

> Section ini ditambahkan oleh Ghaisan Khoirul Badruzaman pada wave 1 mission (18 Mei 2026). Modul `anggota1/anggota1.py` (milik Ghaisan, sesuai roster) tidak diubah, tetapi statusnya sudah deprecated karena drugs.com diblokir oleh Akamai. Section di atas garis pemisah tetap milik Bimo.

### Riwayat sumber data

Sumber data efek samping dan recall obat di MedWatch sempat berubah selama proyek berlangsung:

1. **Versi awal (Maret 2026)**: `anggota1/anggota1.py` melakukan scraping HTML dari `https://www.drugs.com/sfx/<obat>-side-effects.html` dan `https://www.drugs.com/fda-recalls/`.
2. **Mei 2026**: drugs.com migrasi ke proteksi Akamai edge dengan TLS fingerprinting dan header challenge yang memblokir setiap request dari script Python standar dengan HTTP 403 Forbidden. Kutipan langsung dari `anggota1/scraper.log`:
   ```
   [1/2] scraping efek samping (64 obat)
     [1/64] ibuprofen
       status 403
     [2/64] paracetamol
       status 403
   ```
   Sekitar 64 dari 64 URL yang dicoba semua mengembalikan 403; tidak ada satu obat pun yang berhasil di-scrape. File `anggota1/data/drug_safety_data.json` dan `anggota1/data/drug_recalls.json` di-populate dengan fixture sementara dari WHO Essential Medicines monograph agar consumer downstream tidak rusak.
3. **Wave 1 (May 2026)**: pengganti aditif `anggota1/openfda/` dibuat. Modul ini memakai openFDA REST API untuk real large-scale data acquisition. File `anggota1.py` tetap dipertahankan untuk audit trail dan tidak dimodifikasi.

### Endpoint openFDA yang digunakan

| Endpoint | Kegunaan |
|---|---|
| `https://api.fda.gov/drug/event.json` | FDA Adverse Event Reporting System (FAERS). Diakses per-obat dengan parameter `search=patient.drug.medicinalproduct:"<nama>"` dan `count=patient.reaction.reactionmeddrapt.exact` untuk top reaksi, ditambah `count=serious` dan `count=seriousnessdeath` untuk derivasi severity. |
| `https://api.fda.gov/drug/enforcement.json` | FDA Recall / Enforcement Reports. Diakses dengan pagination `skip` dan `limit=1000` (max), diurut `recall_initiation_date:desc`. |

### Dasar legal

openFDA adalah layanan publik gratis yang dioperasikan oleh U.S. Food and Drug Administration. Konsumsi programmatic dengan API key diizinkan untuk penelitian, integrasi sistem informasi kesehatan, dan publikasi (lihat ToS di https://open.fda.gov/license/). Data FAERS dan Enforcement Reports tidak mengandung PII pasien; FDA sudah melakukan de-identifikasi sebelum dipublikasikan. Tidak ada bypass anti-bot, captcha, atau ToS-restricted resource yang dilakukan di pipeline ini.

### Rate-limit handling

- Tanpa API key: 1.000 request / 24 jam per IP, 240 / menit.
- Dengan API key (`OPENFDA_API_KEY` di env, dikirim sebagai query param `api_key`): 120.000 request / 24 jam per IP, 240 / menit.
- Modul memakai polite delay 250 ms antar request dan exponential backoff dengan jitter pada HTTP 429 dan 5xx (maksimum 5 retry, backoff 0.5s -> 1s -> 2s -> 4s -> 8s + jitter).
- HTTP 404 = empty result, lanjut ke obat berikutnya.

### Anti-leak

Nilai `OPENFDA_API_KEY` tidak pernah ditulis ke file disk, log, atau output. Setiap `source_url` di file JSON menampilkan placeholder `&api_key=<redacted>`. Konstanta `OPENFDA_API_KEY` di `api/config.py` hanya membaca dari environment dengan default string kosong; tidak ada nilai hard-coded.

### Cara regenerasi

```bash
cd /path/to/medWatch
export OPENFDA_API_KEY=<your-key-here>
.venv/bin/python -m anggota1.openfda.fetch --max-recall-pages 6
```

Hasilnya ditulis ke `anggota1/data/drug_safety_data.json` dan `anggota1/data/drug_recalls.json` dengan schema yang sama dengan fixture sebelumnya (consumer downstream tidak perlu diubah).

Run wave-1 ini menghasilkan: 74 baris adverse-event (1.850 total reaction-term occurrences) dan 6.000 baris recall. Untuk run yang lebih besar lagi, naikkan `--max-recall-pages` hingga 26 (max sekitar 17.643 record).

Detail teknis lengkap, mapping severity, dan flag CLI tambahan ada di [`anggota1/openfda/README.md`](./anggota1/openfda/README.md).
