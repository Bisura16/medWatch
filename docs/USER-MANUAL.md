---
title: Panduan Pengguna MedWatch (User Manual)
version: 1.0
owner: Kelompok B5, D4 Teknik Informatika, Politeknik Negeri Bandung
date: 2026-05-18
audience: Tenaga kesehatan Faskes 1 (bidan), masyarakat umum, administrator sistem
standar_acuan: ISO/IEC/IEEE 26514:2022 Systems and software engineering, Design and development of information for users
mata_kuliah: Proyek 1 Pengembangan Perangkat Lunak Desktop, Kelas 1B-D4, Semester 2 TA 2025/2026
---

# Panduan Pengguna MedWatch

## 1. Sampul dan Informasi Dokumen

| Atribut | Nilai |
|---|---|
| Judul | Panduan Pengguna Aplikasi MedWatch |
| Versi | 1.0 |
| Tanggal | 18-05-2026 |
| Status | Final, Iterasi 2 |
| Audiens | Tenaga kesehatan (bidan Faskes 1), masyarakat umum, administrator sistem |
| Mata kuliah | Proyek 1 Pengembangan Perangkat Lunak Desktop |
| Kelas | 1B-D4 Teknik Informatika |
| Semester | 2, TA 2025/2026 |
| Kelompok | B5 |
| Standar acuan | ISO/IEC/IEEE 26514:2022 Systems and software engineering, Design and development of information for users |

### Tim Kelompok B5

| Nama | NIM | Peran |
|---|---|---|
| Ghaisan Khoirul Badruzaman | 251524048 | Project Leader, modul anggota1 (scraping) |
| Bimo Surya Anggara | 251524040 | Quality Assurance, modul anggota2 (CRUD pasien SOAP) |
| Alia Ardani | 251524035 | System Analyst, modul anggota3 (visualisasi) |
| Muhammad Iqbal | 251524057 | Programmer, modul anggota4 (drug safety check) |
| Abhidal Muhammad Gazza | 251524032 | UI/UX, modul anggota5 (PDF dan autentikasi) |

### Dosen Pembimbing

- Aprianti Nanda Sari (Project Manager mata kuliah)
- Ade Chandra Nugraha
- Ardhian Ekawijana

### Kepatuhan Dokumentasi

Struktur dan isi dokumen ini disusun mengikuti rekomendasi ISO/IEC/IEEE 26514:2022 untuk dokumentasi pengguna, mencakup:

- identifikasi audiens dan prasyarat pengetahuan (Bagian 1 dan 3),
- prosedur step by step dengan ilustrasi atau placeholder ilustrasi (Bagian 4),
- referensi tugas berdasarkan peran pengguna (Bagian 4.1, 4.2, 4.3),
- daftar pesan kesalahan dengan penjelasan dan tindak lanjut (Bagian 6),
- glossarium istilah teknis (Bagian 8),
- informasi dukungan dan rujukan (Bagian 9 dan 10).

---

## 2. Ringkasan Sistem

MedWatch adalah aplikasi web yang dirancang untuk fasilitas kesehatan tingkat pertama (Faskes 1) guna membantu bidan mengelola rekam medis pasien dengan format SOAP (Subjective, Objective, Assessment, Plan), memantau keamanan obat, melakukan pengecekan interaksi obat, mengekspor laporan dalam bentuk PDF, serta menampilkan visualisasi data efek samping obat. Aplikasi juga menyediakan akses terbatas bagi masyarakat umum untuk pencarian informasi obat dan pengecekan keamanan kombinasi obat secara mandiri. Administrator sistem dapat memantau metrik penggunaan, memicu sinkronisasi katalog obat dari sumber resmi (openFDA), serta mengelola pengguna. MedWatch dijalankan dalam lingkungan web modern menggunakan Next.js untuk antarmuka pengguna dan Flask untuk layanan backend.

---

## 3. Memulai (Getting Started)

### 3.1 Akses Aplikasi

| Lingkungan | URL akses | Keterangan |
|---|---|---|
| Pengembangan lokal | `http://localhost:3000` | Frontend Next.js berjalan dengan `npm run dev` (port 3000). Backend Flask berjalan terpisah di `http://localhost:8080`. Lihat `docs/INSTALL.md` untuk perintah lengkap. |
| Demonstrasi cloud | URL Vercel yang dibagikan oleh Project Leader | Frontend di-deploy pada Vercel; backend di Cloud Run. Cukup akses URL dari peramban yang didukung. |

Tidak diperlukan instalasi pada sisi pengguna selain peramban modern.

![Halaman login MedWatch](screenshots/user-manual/01-login.png)

### 3.2 Login

Halaman `/login` menampilkan dua kolom utama:

1. Kolom kiri berisi judul aplikasi, ringkasan nilai, dan keterangan bahwa kredensial demo tersedia.
2. Kolom kanan berisi formulir Masuk dengan kolom Username dan Password, serta panel "AKUN DEMO" berisi tiga tombol prasetel.

Dua cara masuk ke dalam aplikasi:

- Cara A, manual: ketik Username dan Password pada formulir, lalu tekan tombol Masuk atau tekan tombol Enter pada papan ketik.
- Cara B, kredensial demo: klik salah satu dari tiga kartu prasetel ("Demo Bidan", "Demo Masyarakat", "Demo Admin"). Setelah ditekan, kolom Username dan Password akan terisi otomatis. Tekan tombol Masuk untuk melanjutkan.

Daftar kredensial demo yang ditampilkan pada halaman login (lihat `src/app/login/page.tsx` baris 18 sampai 43):

| Peran | Tombol prasetel | Username | Diarahkan ke |
|---|---|---|---|
| Tenaga Kesehatan (bidan) | Demo Bidan | `bidan_siti` | `/dashboard` |
| Masyarakat Umum | Demo Masyarakat | `umum_budi` | `/drug-search` |
| Administrator Sistem | Demo Admin | `admin_ghaisan` | `/admin/dashboard` |

Nilai password ditampilkan langsung pada halaman login dalam kolom prasetel sebagai bagian dari mode demo (lihat juga Bagian 7 FAQ untuk diskusi keamanan akun demo). Untuk akses produksi, kredensial harus diganti dan tidak boleh dimuat ke dalam UI.

![Klik kartu Demo Bidan untuk auto-isi](screenshots/user-manual/02-demo-preset.png)

### 3.3 Persyaratan Peramban

| Peramban | Versi minimum yang disarankan |
|---|---|
| Google Chrome | 119 atau lebih baru |
| Mozilla Firefox | 118 atau lebih baru |
| Safari | 17 atau lebih baru |
| Microsoft Edge | 119 atau lebih baru |

Persyaratan tambahan: koneksi internet aktif (aplikasi tidak mendukung mode offline untuk versi web), JavaScript aktif, dan kebijakan cookie pihak ketiga tidak diblokir penuh (token autentikasi disimpan pada cookie httpOnly dengan SameSite, lihat `docs/SECURITY.md`).

---

## 4. Panduan per Peran

### 4.1 Peran Tenaga Kesehatan (Bidan)

Bidan memiliki akses penuh ke seluruh fitur manajemen pasien, pengecekan keamanan obat, ekspor laporan, dan visualisasi.

#### 4.1.1 Login sebagai Bidan

1. Buka `/login`.
2. Klik kartu "Demo Bidan" untuk mengisi otomatis, atau ketik manual `bidan_siti` pada kolom Username dan kredensial demo yang sesuai pada kolom Password.
3. Tekan tombol Masuk.
4. Sistem otomatis mengarahkan ke `/dashboard`.

![Login bidan berhasil](screenshots/user-manual/03-login-bidan.png)

#### 4.1.2 Beranda Dashboard

Dashboard menampilkan:

- ringkasan KPI klinik (jumlah pasien terdaftar, kunjungan periode berjalan, jumlah resep aktif),
- daftar pasien terakhir yang ditangani (sudah diurutkan dengan kunjungan terbaru di atas, sesuai perbaikan B07),
- pintasan aksi cepat menuju formulir pasien baru, cek interaksi obat, dan ekspor PDF.

![Dashboard bidan](screenshots/user-manual/04-dashboard-bidan.png)

#### 4.1.3 CRUD Pasien dengan Format SOAP

##### Menambah Pasien Baru

1. Klik tombol Tambah Pasien pada Dashboard, atau navigasi ke `/patients/new`.
2. Isi bagian 1 Identitas:
   - Nama (wajib),
   - Umur (opsional),
   - Alamat (opsional),
   - Kategori (opsional, contoh: Ibu Hamil, KB, Anak),
   - Tanggal Kunjungan (format dd-MM-yyyy, default hari ini).
3. Isi bagian 2 S Subjective (wajib): kolom Keluhan wajib diisi. Kolom Riwayat opsional.
4. Isi bagian 3 O Objective: tekanan darah (format `123/80`), BB (kg), tb (cm), lila (cm), Nadi (x/menit), Suhu (°C), Respirasi (x/menit), serta catatan tambahan. Seluruh nilai numerik divalidasi pada saat ketik (perbaikan B03): huruf ditolak otomatis dan rentang nilai diperiksa terhadap `NUMERIC_RANGES` (lihat `src/lib/patient-validation.ts`).
5. Isi bagian 4 A Assessment (wajib): kolom Diagnosa wajib diisi.
6. Isi bagian 5 P Plan (wajib): kolom Tindakan wajib diisi. Kolom Resep dan Jadwal Kontrol opsional.
7. Tekan tombol Simpan SOAP. Setelah berhasil, sistem mengarahkan ke halaman detail pasien `/patients/<id>`.

![Form pasien baru, bagian SOAP](screenshots/user-manual/05-patient-new-form.png)

##### Membuka, Mengedit, dan Menghapus Pasien

1. Navigasi ke `/patients`. Daftar pasien tampil dengan kunjungan terbaru di atas (B07).
2. Klik baris pasien untuk membuka detail `/patients/<id>`.
3. Pada halaman detail, tombol Edit membuka formulir yang sama dengan data terisi. Setelah disunting, tekan Simpan SOAP.
4. Tombol Hapus pada halaman detail menampilkan dialog konfirmasi sebelum penghapusan permanen.

![Daftar pasien diurut terbaru di atas](screenshots/user-manual/06-patient-list.png)

##### Validasi Field Medis Numerik (B03)

Jika seorang pengguna mengetik huruf pada kolom BB, sistem menolak input dan menampilkan pesan singkat di bawah kolom. Contoh:

- Input pada kolom BB: `abc` -> sistem menolak ketikan huruf.
- Input pada kolom BB: `500` -> muncul pesan `BB di luar rentang wajar (1 sampai 200 kg)`.
- Input pada kolom Tekanan Darah: `9999` (tanpa garis miring) -> tombol Simpan dinonaktifkan dan muncul pesan format yang diharapkan `123/80`.

Validasi serupa berlaku untuk Tinggi Badan (tb_cm), Lingkar Lengan Atas (lila_cm), Nadi, Suhu, dan Respirasi.

![Pesan validasi numerik pada bagian Objective](screenshots/user-manual/07-validation-error.png)

#### 4.1.4 Cek Interaksi Obat (Safety Checker)

Halaman `/safety-checker` membantu bidan mengevaluasi keamanan kombinasi obat untuk seorang pasien.

Langkah-langkah:

1. Navigasi ke `/safety-checker` atau pintasan dari Dashboard.
2. Pada panel sebelah kiri, blok "1 - Pilih pasien" menampilkan empat pasien teratas. Klik salah satu untuk memilih.
3. Setelah pasien dipilih, panel "Obat aktif pasien" muncul dan otomatis berisi obat yang sedang dikonsumsi pasien (diambil dari kolom Resep pada SOAP kunjungan terakhir; perbaikan B05). Obat-obat ini ditambahkan ke daftar obat yang akan dipindai.
4. Pada blok "2 - Tambah obat untuk diskrining", ketik nama obat pada kolom pencarian. Saran obat akan muncul dari katalog (sumber: openFDA + agregasi internal). Pilih saran untuk menambahkan.
5. Untuk menghapus obat dari daftar, klik tanda silang pada chip obat.
6. Tekan tombol "Pindai keamanan".
7. Hasil tampil di panel kanan. Bagian "VERDIKT" menampilkan label aggregate severity. Bagian di bawahnya berisi kartu per pasangan obat atau per efek samping.

![Pemilihan pasien dengan obat aktif terdeteksi](screenshots/user-manual/08-safety-patient.png)

![Hasil pemindaian dengan VERDIKT dan kartu interaksi](screenshots/user-manual/09-safety-result.png)

Cara membaca VERDIKT (lihat juga Bagian 5.1):

- `severity_score` dihitung dari bobot keparahan setiap efek (ringan = 1, sedang = 2, serius = 4), dinormalisasi ke skala 0 sampai 100.
- `label_risiko`: `low` untuk skor di bawah 40, `medium` untuk skor 40 sampai 69, `high` untuk skor 70 ke atas.
- Label di kartu utama VERDIKT mengikuti `severity_level` yang ditampilkan sebagai AMAN, PERHATIAN RINGAN, PERHATIAN SEDANG, atau BAHAYA SERIUS.
- Kartu per interaksi menampilkan nama obat, kategori (alergi, vs obat aktif, atau pasangan), tingkat keparahan, dan deskripsi efek.
- Panel bantuan "Cara membaca verdikt dan obat aktif" tersedia di bagian atas hasil dan dapat dibuka tutup.

#### 4.1.5 Export PDF

Halaman `/export-pdf` menyediakan empat jenis laporan (perbaikan B04, seluruh jenis sudah berfungsi):

| ID Laporan | Nama tampilan | Endpoint backend | Argumen |
|---|---|---|---|
| `rekam-medis` | Riwayat SOAP per pasien | `/api/pdf/generate-rekam-medis` | `pasien_id` |
| `laporan-bulanan` | Rekap kunjungan bulanan | `/api/pdf/generate-laporan-bulanan` | `month` (format `YYYY-MM`) |
| `efek-samping` | Laporan efek samping obat | `/api/pdf/generate-efek-samping` | tidak ada |
| `inventaris` | Inventaris obat | `/api/pdf/generate-inventaris` | tidak ada |

Langkah-langkah:

1. Navigasi ke `/export-pdf`.
2. Pada blok "1 - Jenis laporan", pilih salah satu dari empat opsi.
3. Pada blok "2", lengkapi argumen sesuai jenis: pilih pasien dari dropdown untuk Rekam Medis, atau pilih periode dd-MM-yyyy untuk Laporan Bulanan. Jenis Efek Samping dan Inventaris tidak memerlukan argumen.
4. Tekan tombol "Generate Laporan". Saat selesai, peramban otomatis mengunduh berkas PDF dengan nama: `rekam-medis-<id>.pdf`, `laporan-bulanan-<YYYY-MM>.pdf`, `laporan-efek-samping.pdf`, atau `laporan-inventaris-obat.pdf`.

![Pilih jenis laporan PDF](screenshots/user-manual/10-export-pdf.png)

#### 4.1.6 Visualisasi

Halaman `/visualization` menampilkan kumpulan grafik:

- Heatmap obat x efek samping di `/heatmap`,
- Tren kunjungan per periode,
- Top efek samping obat terlapor.

##### Heatmap (B11)

1. Navigasi ke `/heatmap`.
2. Heatmap menampilkan matriks dengan baris berisi obat dan kolom berisi efek samping. Intensitas warna mengikuti skala kontinu (perbaikan B11): semakin tua warna, semakin tinggi nilai sel.
3. Baris dan kolom diurutkan menurun sesuai total intensitas, sehingga obat dan efek dengan beban tertinggi muncul di sudut kiri atas.
4. Arahkan kursor ke sel untuk melihat tooltip berisi nama obat, nama efek, dan nilai numerik.
5. Sel kosong atau tidak tersedia ditandai dengan pola garis miring dan label `N/A`.
6. Legenda gradien di bawah matriks menampilkan rentang minimum, tengah, dan maksimum nilai.

![Heatmap obat x efek samping dengan skala kontinu](screenshots/user-manual/11-heatmap.png)

##### Tren Kunjungan dan Top Efek Samping

Pada halaman `/visualization`, grafik garis menampilkan jumlah kunjungan per bulan. Grafik batang menampilkan sepuluh efek samping terbanyak terlapor lengkap dengan warna berdasar tingkat keparahan (hijau untuk ringan, kuning untuk sedang, merah untuk serius).

![Tren kunjungan dan top efek samping](screenshots/user-manual/12-visualization.png)

#### 4.1.7 Logout

Klik menu profil pada bilah navigasi, lalu pilih Keluar. Sesi dihapus pada sisi peramban dan cookie autentikasi diinvalidasi. Pengguna diarahkan kembali ke `/login`.

---

### 4.2 Peran Masyarakat Umum

Pengguna kategori masyarakat memiliki cakupan terbatas, fokus pada pencarian informasi obat dan pengecekan keamanan kombinasi obat untuk diri sendiri.

#### 4.2.1 Login sebagai Masyarakat

1. Buka `/login`.
2. Klik kartu "Demo Masyarakat" atau ketik manual `umum_budi`.
3. Tekan tombol Masuk.
4. Sistem otomatis mengarahkan ke `/drug-search`.

![Login masyarakat berhasil](screenshots/user-manual/13-login-masyarakat.png)

#### 4.2.2 Drug Search

Halaman `/drug-search` menyediakan pencarian katalog obat:

1. Ketik nama obat (contoh: paracetamol) pada kolom pencarian.
2. Daftar saran muncul dengan menampilkan nama obat, nama generik, dan kelas terapi.
3. Klik hasil untuk membuka detail.
4. Halaman detail menampilkan: nama, nama generik, kelas, indikasi, dosis lazim, peringatan, dan daftar efek samping dengan tingkat keparahan.

![Daftar hasil pencarian obat](screenshots/user-manual/14-drug-search-list.png)

![Detail obat dengan peringatan](screenshots/user-manual/15-drug-search-detail.png)

#### 4.2.3 Cek Interaksi Obat (Mode Tanpa Pasien)

1. Navigasi ke `/safety-checker`.
2. Karena peran adalah masyarakat, blok pemilihan pasien tidak ditampilkan (lihat `src/app/safety-checker/page.tsx` baris 384, kondisi `!isMasyarakat`).
3. Tambahkan obat melalui kolom pencarian.
4. Tekan tombol "Pindai keamanan".
5. Verdikt dan kartu hasil tampil dengan logika yang sama seperti pada peran bidan.

![Safety checker mode masyarakat](screenshots/user-manual/16-safety-masyarakat.png)

#### 4.2.4 Profil Pribadi

Halaman `/pasien/profile` menampilkan ringkasan profil pengguna (nama, kontak, dan tanggal pendaftaran). Pengguna masyarakat hanya dapat melihat profilnya sendiri.

![Halaman profil masyarakat](screenshots/user-manual/17-profile-masyarakat.png)

#### 4.2.5 Logout

Klik menu profil pada bilah navigasi lalu pilih Keluar.

---

### 4.3 Peran Administrator Sistem

Administrator memiliki akses ke panel sistem, pemicuan scraper, dan manajemen pengguna.

#### 4.3.1 Login sebagai Admin

1. Buka `/login`.
2. Klik kartu "Demo Admin" atau ketik manual `admin_ghaisan`.
3. Tekan tombol Masuk.
4. Sistem otomatis mengarahkan ke `/admin/dashboard`.

![Login admin berhasil](screenshots/user-manual/18-login-admin.png)

#### 4.3.2 Admin Dashboard

Halaman `/admin/dashboard` menampilkan KPI nyata yang ditarik dari endpoint backend `/api/admin/system-stats` (perbaikan B10). Lihat `src/app/admin/dashboard/page.tsx` baris 39 sampai 54. KPI yang ditampilkan:

- Pengguna aktif (memuat ringkasan jumlah bidan dan masyarakat di subteks),
- Pasien terdaftar,
- Obat di katalog (memuat info update terakhir bila tersedia),
- Uptime API (dihitung dari `uptime_seconds` proses backend).

Bagian Aksi cepat menampilkan kartu "Jalankan Scraper Obat" dengan tombol "Buka panel scraper" yang mengarah ke `/admin/scraper` (perbaikan B01). Bagian Audit log menampilkan aktivitas terakhir.

![Admin dashboard dengan KPI nyata](screenshots/user-manual/19-admin-dashboard.png)

#### 4.3.3 Aktivitas Terbaru dan "Lihat Semua"

Pintasan "Lihat semua" sudah berfungsi (perbaikan B02) dan mengarah ke `/dashboard/aktivitas`. Halaman tersebut menampilkan log aktivitas pengguna dengan filter periode.

![Halaman aktivitas terbaru](screenshots/user-manual/20-aktivitas.png)

#### 4.3.4 Memicu Scraper openFDA

1. Pada `/admin/dashboard`, klik tombol "Buka panel scraper".
2. Halaman `/admin/scraper` menampilkan daftar job scraping. Setiap baris memiliki tombol Trigger.
3. Tekan tombol Trigger pada baris yang dipilih, contoh "openFDA - sinkronisasi katalog obat".
4. Permintaan dikirim ke endpoint backend `POST /api/admin/scrape` (lihat `api/routes/admin_routes.py` baris 21 sampai 26). Status job berubah menjadi running.
5. Setelah selesai, status berubah menjadi success, hitungan entri terbaru tampil, dan KPI "Obat di katalog" pada Dashboard akan ter-refresh setelah halaman dimuat ulang.

![Panel scraper admin](screenshots/user-manual/21-admin-scraper.png)

Catatan: pemicu pada panel ini terhubung ke modul `anggota1` melalui adapter. Eksekusi manual dapat dilakukan pada sisi server dengan perintah `python -m anggota1.openfda.fetch`, lihat `docs/INSTALL.md`.

#### 4.3.5 Manage Users

Halaman `/admin/users` menampilkan tabel pengguna dengan kolom Username, Nama, Peran, Telepon, dan tombol aksi. Admin dapat menyetujui permintaan pendaftaran, mengubah peran, dan menonaktifkan akun. Operasi tunduk pada validasi backend (lihat `api/routes/admin_routes.py`).

![Manajemen pengguna](screenshots/user-manual/22-admin-users.png)

#### 4.3.6 Logout

Klik menu profil pada bilah navigasi lalu pilih Keluar.

---

## 5. Operasi Lanjutan

### 5.1 Cara Membaca Verdikt Safety Check

Hasil dari `POST /api/safety/check` mengandung tiga keluaran utama:

1. `severity_score` (angka 0 sampai 100), `severity_level` (`low`, `medium`, `high`), dan `warnings`.
2. Daftar `drugs` per obat lengkap dengan `skor_risiko`, `label_risiko`, `ringkasan_keparahan` (hitungan serius, sedang, ringan), dan `efek_dikenali`.
3. Daftar `interactions` per pasangan obat dengan `tingkat_tertinggi`.

Logika dasar (lihat panel bantuan in-app pada `src/app/safety-checker/page.tsx` baris 776 sampai 788):

- Setiap efek samping diberi bobot keparahan: ringan = 1, sedang = 2, serius = 4.
- Total bobot dibagi bobot maksimum (jumlah efek dikali 4) menghasilkan skor 0 sampai 100.
- Skor di bawah 40 berlabel risiko rendah. Skor 40 sampai 69 berlabel sedang. Skor 70 atau lebih berlabel tinggi.
- VERDIKT pada kartu utama adalah label tertinggi di antara semua obat dan interaksi yang dicek.

Pemetaan label internal ke label tampilan:

| `severity_level` backend | Label utama | Sub label |
|---|---|---|
| `low` (dengan kartu) | PERHATIAN RINGAN | Interaksi minor; pantau sendiri |
| `low` (tanpa kartu) | AMAN | Tidak ada interaksi terdeteksi |
| `medium` | PERHATIAN SEDANG | Sesuaikan dosis atau pantau ketat |
| `high` | BAHAYA SERIUS | Hindari kombinasi atau ganti obat |

Kartu per interaksi diberi warna sesuai tingkat keparahan: hijau untuk ringan, kuning untuk sedang, merah untuk serius.

### 5.2 Cara Membaca Heatmap

Heatmap pada `/heatmap` (lihat `src/app/heatmap/page.tsx`):

- Baris = nama obat. Kolom = nama efek samping.
- Nilai sel = presensi efek dikali bobot keparahan: ringan = 1, sedang = 2, serius = 4. Bila data sumber bersifat presensi atau absensi murni (1 atau 0), nilai diskalakan oleh bobot keparahan kolom; bila nilai sumber sudah menyandang magnitudo, nilai dikalikan bobot lalu dibulatkan.
- Skala warna kontinu dibangun dari `buildColorScale(min, max)` dengan minimum berwarna terang dan maksimum berwarna gelap.
- Baris dan kolom diurutkan menurun berdasarkan total, sehingga obat dan efek dengan beban tertinggi muncul di sudut kiri atas matriks.
- Tooltip pada `hover` menampilkan `<nama obat> x <nama efek>: <nilai>`.
- Legenda di bawah matriks menampilkan rentang min, tengah, max, serta keterangan sel N/A bila data tidak tersedia.

### 5.3 Cara Membaca Grafik Visualisasi Lainnya

- Grafik tren kunjungan (line chart): sumbu X bulan, sumbu Y jumlah kunjungan, satu garis untuk total kunjungan dan satu garis terputus untuk kunjungan ibu hamil.
- Grafik top efek samping (bar chart horizontal): sumbu Y nama efek, sumbu X jumlah laporan, warna batang berdasar tingkat keparahan (hijau, kuning, merah).

---

## 6. Penanganan Kesalahan (Common Errors)

Daftar pesan kesalahan yang umum muncul beserta penjelasan dan tindak lanjut.

| Lokasi | Pesan / Status | Arti | Tindak lanjut pengguna |
|---|---|---|---|
| Halaman login | `Kredensial tidak cocok dengan akun demo.` (status backend 401) | Username atau password salah | Periksa ulang ejaan. Gunakan kartu prasetel pada panel "AKUN DEMO" untuk mengisi otomatis. |
| Halaman login | `Username dan password wajib diisi.` | Salah satu kolom kosong saat tombol Masuk ditekan | Isi kedua kolom lalu coba lagi. |
| Form pasien baru | `Field nama, keluhan (S), diagnosa (A), dan tindakan (P) wajib diisi.` | Salah satu kolom wajib SOAP belum diisi | Isi semua kolom wajib yang ditandai. |
| Form pasien baru | `Periksa kembali nilai numerik pada bagian Objective.` | Salah satu kolom numerik di luar rentang atau berisi karakter ilegal | Lihat pesan inline per kolom (di bawah input) untuk detail. |
| Form pasien baru, kolom BB | `BB di luar rentang wajar` | Nilai di luar `NUMERIC_RANGES.bb_kg` | Masukkan nilai antara 1 sampai 200 kg. |
| Form pasien baru, kolom Tekanan Darah | Validasi `pattern \d{1,3}/\d{1,3}` gagal | Format harus `sistolik/diastolik` | Gunakan format misalnya `120/80`. |
| Safety checker | `Gagal memindai keamanan` | Permintaan ke `/api/safety/check` gagal | Periksa konektivitas, ulangi pemindaian. |
| Akses `/admin/*` dengan peran bukan admin | Halaman redirect ke `/login?from=...` atau tampil pesan 403 | RBAC backend menolak | Login ulang dengan akun admin atau hubungi administrator. |
| Sesi habis | Otomatis redirect ke `/login?from=<rute terakhir>` | JWT pada cookie sudah kedaluwarsa | Login ulang. Sistem akan mengembalikan ke halaman semula bila aman. |
| Export PDF | `Pilih pasien terlebih dahulu` | Jenis laporan `rekam-medis` dipilih tanpa memilih pasien | Pilih pasien dari dropdown. |
| Export PDF | `Gagal membuat PDF` | Permintaan ke endpoint `/api/pdf/...` gagal | Coba ulangi. Bila tetap gagal, hubungi administrator. |
| Heatmap | `Data backend tidak tersedia. Menampilkan contoh fallback.` (warna kuning kecil) | Endpoint `/api/visualizations/heatmap-efek` tidak merespons | Heatmap menampilkan matriks fallback deterministik untuk uji visual. Hubungi administrator untuk memuat ulang data. |

---

## 7. FAQ

### 7.1 Apakah data pasien saya aman?

Singkat: ya, dengan batasan berikut.

- Autentikasi menggunakan JSON Web Token (JWT) yang dikemas dalam cookie httpOnly dengan flag SameSite, sehingga JavaScript di sisi peramban tidak bisa membaca token secara langsung.
- Kata sandi pengguna disimpan dalam bentuk hash bcrypt dengan cost factor 12 (tidak dalam bentuk plaintext).
- Komunikasi antara peramban, frontend Vercel, dan backend Cloud Run terenkripsi via HTTPS.
- Kebijakan CORS pada backend dibatasi pada daftar origin yang diizinkan.
- Tidak ada berkas service-account key yang disimpan di repositori; rahasia disuntikkan melalui environment variable.

Rincian lengkap kebijakan keamanan, peta OWASP Top 10, dan analisis STRIDE per aset tersedia pada `docs/SECURITY.md`.

### 7.2 Apakah aplikasi bisa digunakan offline?

Tidak untuk versi web saat ini. Versi web membutuhkan koneksi internet aktif untuk memuat aplikasi Next.js, memanggil API Flask, dan mengakses katalog obat. Rencana dukungan offline (desktop installer) didokumentasikan pada `ProductionGrade-ImplementationPlan/02-offline-implementation-plan.md`.

### 7.3 Bagaimana memperbarui data obat?

Dua cara, sesuai peran:

- Administrator: login, buka `/admin/scraper`, lalu tekan tombol Trigger pada job sinkronisasi katalog. Endpoint backend yang dipicu adalah `POST /api/admin/scrape` (lihat `api/routes/admin_routes.py` baris 21 sampai 26).
- Eksekusi sisi server (untuk pengembang atau administrator dengan akses terminal): jalankan `python -m anggota1.openfda.fetch`. Modul ini melakukan pengambilan data dari openFDA dengan API key yang dibaca dari environment variable `OPENFDA_API_KEY`. Lihat `docs/INSTALL.md` untuk detail.

### 7.4 Bahasa antarmuka bisa diubah?

Saat ini antarmuka hanya tersedia dalam Bahasa Indonesia. Lokal tanggal mengikuti format dd-MM-yyyy.

### 7.5 Bagaimana jika lupa kata sandi?

Untuk akun demo, kredensial tertera pada kartu prasetel halaman `/login`. Untuk akun produksi, prosedur reset kata sandi dikelola oleh administrator sistem; hubungi melalui kontak pada Bagian 9.

---

## 8. Glossarium

| Istilah | Definisi |
|---|---|
| Tenaga Kesehatan | Peran sistem untuk bidan Faskes 1; memiliki akses penuh ke CRUD pasien, safety checker, ekspor PDF, dan visualisasi. Nilai internal `tenaga_kesehatan`. |
| Masyarakat | Peran sistem untuk pengguna umum non-klinis; memiliki akses terbatas pada pencarian obat dan safety check mandiri. Nilai internal `masyarakat`. |
| Admin | Peran sistem untuk administrator; memiliki akses panel sistem, pemicuan scraper, dan manajemen pengguna. Nilai internal `admin`. |
| SOAP | Format dokumentasi medis: Subjective (keluhan dan riwayat pasien), Objective (temuan pemeriksaan fisik dan vital sign), Assessment (diagnosa), Plan (rencana tindakan dan resep). |
| Faskes 1 | Fasilitas kesehatan tingkat pertama, contoh: puskesmas, klinik pratama, posyandu. Pengguna inti MedWatch. |
| JWT | JSON Web Token, format token autentikasi standar (RFC 7519). MedWatch menyimpan JWT dalam cookie httpOnly dengan SameSite. |
| openFDA | API publik U.S. Food and Drug Administration untuk data obat, recall, dan efek samping. Sumber data utama MedWatch setelah pivot dari drugs.com (lihat ADR-004). |
| FAERS | FDA Adverse Event Reporting System, basis data efek samping obat yang dikelola FDA dan tersedia melalui openFDA. |
| Recall classification | Klasifikasi recall obat oleh FDA: Class I (potensi bahaya serius hingga kematian), Class II (efek sementara), Class III (kemungkinan pelanggaran regulasi tanpa efek kesehatan). |
| Verdikt | Label aggregate keamanan dari safety checker; AMAN, PERHATIAN RINGAN, PERHATIAN SEDANG, atau BAHAYA SERIUS, dipetakan dari `severity_level` backend (`low`, `medium`, `high`). |
| BPOM | Badan Pengawas Obat dan Makanan Republik Indonesia, regulator obat di Indonesia. |
| WHO | World Health Organization, organisasi kesehatan dunia. |
| RBAC | Role Based Access Control, kontrol akses berbasis peran. |
| dd-MM-yyyy | Format tanggal Indonesia (dua digit hari, dua digit bulan, empat digit tahun). Format default semua kolom tanggal MedWatch. |

---

## 9. Kontak dan Dukungan

| Saluran | Tujuan | Penerima |
|---|---|---|
| Project Leader Kelompok B5 | Pertanyaan teknis dan eskalasi insiden | Ghaisan Khoirul Badruzaman (NIM 251524048) |
| Quality Assurance | Bug report dan permintaan pengujian ulang | Bimo Surya Anggara (NIM 251524040) |
| System Analyst | Klarifikasi kebutuhan dan visualisasi | Alia Ardani (NIM 251524035) |
| Programmer (drug safety) | Pertanyaan logika safety check | Muhammad Iqbal (NIM 251524057) |
| UI/UX (PDF dan autentikasi) | Pertanyaan terkait tampilan, login, dan ekspor PDF | Abhidal Muhammad Gazza (NIM 251524032) |
| Dosen Pembimbing | Pertanyaan akademik dan asesmen | Aprianti Nanda Sari, Ade Chandra Nugraha, Ardhian Ekawijana |

Saluran lapor:

- Sistem internal kelompok via repositori GitHub (Issues).
- Tatap muka pada sesi mata kuliah Proyek 1 Pengembangan Perangkat Lunak Desktop.

---

## 10. Referensi

1. ISO/IEC/IEEE 26514:2022, Systems and software engineering, Design and development of information for users.
2. ISO/IEC/IEEE 15289:2019, Systems and software engineering, Content of life-cycle information items (documentation).
3. ISO/IEC/IEEE 29148:2018, Systems and software engineering, Life cycle processes, Requirements engineering. (Diacu pada `docs/SRS.md`.)
4. IEEE 1016-2009, IEEE Standard for Information Technology, Systems Design, Software Design Descriptions. (Diacu pada `docs/SDD.md`.)
5. Dokumen MedWatch terkait:
   - `docs/PRD.md` Product Requirements Document.
   - `docs/SRS.md` Software Requirements Specification.
   - `docs/SDD.md` Software Design Description.
   - `docs/API.md` API documentation.
   - `docs/DATA-DICTIONARY.md` Data dictionary dan storage.
   - `docs/INSTALL.md` Install, deploy, dan dev guide.
   - `docs/SECURITY.md` Security and threat model.
   - `docs/adr/` Architecture Decision Records (MADR).
6. Sumber data eksternal:
   - openFDA API, https://open.fda.gov/apis/
   - BPOM Republik Indonesia, https://cekbpom.pom.go.id/
   - WHO, https://www.who.int/
7. Modul anggota proyek:
   - `anggota1/` modul scraping (Ghaisan).
   - `anggota2/` modul CRUD pasien SOAP (Bimo).
   - `anggota3/` modul visualisasi termasuk `NewestVisualization/` (Alia).
   - `anggota4/` modul drug safety check (Iqbal).
   - `anggota5/` modul PDF dan autentikasi (Abhidal).

---

Catatan: tangkapan layar (screenshot) untuk seluruh placeholder pada manual ini akan diisi pada Iterasi 5 setelah lingkungan Node 22 LTS disiapkan, sebagaimana didokumentasikan pada blocker `B-BUILD-1`. Sampai saat itu, placeholder bersifat informatif dan menunjuk pada lokasi rendering yang dijanjikan di bawah `screenshots/user-manual/`.
