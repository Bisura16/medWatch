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
