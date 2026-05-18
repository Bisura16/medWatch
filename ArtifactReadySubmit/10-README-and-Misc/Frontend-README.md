# MedWatch Frontend - Next.js 15 Web Showcase for the MedWatch Desktop System

> Antarmuka web showcase yang membungkus modul desktop MedWatch (anggota1-5) lewat REST API berbasis Flask. Frontend ini Next.js 16 App Router yang dideploy ke Vercel dengan proxy ke backend Flask di Google Cloud Run.

| Metadata | Nilai |
|---|---|
| Mata kuliah | Proyek 1 Pengembangan Perangkat Lunak Desktop |
| Institusi | Politeknik Negeri Bandung, D4 Teknik Informatika, Kelas 1B-D4 |
| Tahun Akademik | Semester 2, TA 2025/2026 |
| Kelompok | B5 |
| Submission | 25 Mei 2026 |
| Live frontend | https://medwatch-frontend.vercel.app |
| Live backend | https://medwatch-api-517694123086.asia-southeast1.run.app |
| Backend repo | https://github.com/Bisura16/medWatch |

---

## 1. Apa Itu Frontend MedWatch

Frontend MedWatch adalah web showcase yang memvisualisasikan fungsi sistem desktop MedWatch (lima modul Python anggota1-5) lewat browser. Frontend ini tidak menggantikan aplikasi desktop CustomTkinter milik kelompok; ia adalah lapisan presentasi tambahan ("demo fitur, bukan demo aplikasi") yang menghubungkan REST API backend (Flask di Cloud Run) ke antarmuka modern berbasis Next.js 16, Tailwind v4, dan shadcn/ui. Posisi web layer dalam keseluruhan sistem dijelaskan di repo backend pada file [SDD.md](https://github.com/Bisura16/medWatch/blob/main/docs/SDD.md) dan [AS-BUILT.md](https://github.com/Bisura16/medWatch/blob/main/docs/AS-BUILT.md).

Frontend ini berfokus pada visualisasi data kesehatan, manajemen pasien dengan skema SOAP, pencarian obat, pengecekan keamanan obat multi-input, heatmap obat-efek kontinu, ekspor laporan PDF, dan administrasi pengguna.

---

## 2. Tim Pengembang

| Nama | NIM | Peran | Modul | GitHub |
|---|---|---|---|---|
| Ghaisan Khoirul Badruzaman | 251524048 | Project Leader, Team Coordinator | anggota1 (scraping + openFDA acquisition) | Finerium |
| Bimo Surya Anggara | 251524040 | Quality Assurance | anggota2 (CRUD pasien SOAP) | Bisura16 |
| Alia Ardani | 251524035 | System Analyst | anggota3 (visualisasi matplotlib + NewestVisualization) | vssixla |
| Muhammad Iqbal | 251524057 | Programmer | anggota4 (drug safety check) | BallVoldigoad |
| Abhidal Muhammad Gazza | 251524032 | UI/UX Designer | anggota5 (PDF export fpdf2 + auth) | Heimdall |

Dosen pendamping: Aprianti Nanda Sari (Project Manager), Ade Chandra Nugraha, Ardhian Ekawijana.

---

## 3. Fitur Utama

Daftar fitur disusun mengikuti ID requirement dari [SRS](https://github.com/Bisura16/medWatch/blob/main/docs/SRS.md) backend. ID requirement (FR-NNN) dapat ditelusuri ke baris implementasi di kedua repo via Requirements Traceability Matrix.

1. **Autentikasi tiga peran** (FR-001 sampai FR-008): halaman `/login` dengan tiga preset demo (tenaga_kesehatan, masyarakat, admin), pembacaan kredensial dari `FormData` untuk kompatibilitas password manager, middleware Next.js untuk redirect dan role gating pada `/admin/*` dan `/pasien/*`.
2. **CRUD pasien SOAP** (FR-010 sampai FR-019): daftar pasien `/patients` terurut newest-first, form bidan-style di `/patients/new` dengan validasi range klinis pada blur dan submit, detail printable di `/patients/[id]`.
3. **Pencarian obat dan perbandingan** (FR-020 sampai FR-024): autocomplete dengan alias di `/drug-search`, side-by-side comparison di `/drug-compare`, profil keamanan lengkap per obat.
4. **Pengecekan keamanan obat** (FR-030 sampai FR-039): multi-input chip di `/safety-checker`, otomatis menyertakan obat aktif pasien jika `pasien_id` dipilih, panel edukasi cara membaca verdict severitas.
5. **Visualisasi data** (FR-040 sampai FR-049): tren kunjungan, distribusi kategori, top efek samping di `/visualization`; heatmap obat x efek dengan skala warna kontinu 5-stop dan legend gradient di `/heatmap`.
6. **Ekspor PDF** (FR-050 sampai FR-054): empat tipe laporan di `/export-pdf` (rekam medis, kunjungan bulanan, efek samping ter-ranked, inventaris obat), setiap tipe memanggil endpoint backend yang berbeda.
7. **Admin tooling** (FR-060 sampai FR-069): trigger scraper di `/admin/scraper`, manajemen pengguna di `/admin/users` dengan proteksi penghapusan admin terakhir, dashboard sistem di `/admin/dashboard`.
8. **Profile masyarakat** di `/pasien/profile` untuk peran masyarakat (akses terbatas rekam medis miliknya).

Daftar requirement non-functional (performance, accessibility, i18n) lengkap di [SRS](https://github.com/Bisura16/medWatch/blob/main/docs/SRS.md) bagian 4.

---

## 4. Tech Stack

Sumber versi: [`package.json`](./package.json).

| Library | Versi | Kegunaan |
|---|---|---|
| Next.js | 16.2.1 | React framework dengan App Router dan Turbopack |
| React | 19.2.4 | UI library |
| TypeScript | 5.x strict | Type safety |
| Tailwind CSS | v4 | Utility-first styling |
| shadcn/ui | latest | Radix-based component primitives |
| @base-ui/react | 1.3.x | Komponen low-level Base UI |
| Recharts | 3.8.x | Visualisasi chart |
| Framer Motion | 12.x | Animasi |
| Zustand | 5.x | Client state (auth, patient) |
| next-themes | 0.4.x | Dark/light mode |
| d3-scale | 4.x | Skala warna kontinu untuk heatmap |
| jspdf | 4.x | PDF download helper |
| Three.js + React Three Fiber | latest | Archived molecule viewer |
| react-force-graph-2d | 1.29.x | Archived drug network graph |
| react-simple-maps + topojson | latest | Archived Indonesia map |

Dependency lengkap dengan exact range ada di [`package.json`](./package.json).

---

## 5. Arsitektur

Frontend tidak berbicara langsung dengan Cloud Run. Semua request `/api/...` dirutekan via proxy di [`src/proxy.ts`](./src/proxy.ts) (Next.js 16 ekuivalen dari pre-16 `middleware.ts`) yang:

1. Memforward request ke `BACKEND_API_URL` (server-only env var, tidak pernah expose ke browser).
2. Menyertakan JWT dari cookie httpOnly `medwatch_token` sebagai header `Authorization: Bearer ...`.
3. Pada `/api/auth/login`, men-set cookie dari field `token` di response backend.
4. Pada `/api/auth/logout`, menghapus cookie.

### Diagram C4 Level 1 (System Context)

![C4 Level 1 Context: aktor tenaga kesehatan, masyarakat, admin terhubung ke MedWatch melalui Vercel frontend; MedWatch terkoneksi ke openFDA API dan GCS state bucket](https://raw.githubusercontent.com/Bisura16/medWatch/main/docs/diagrams/png/c4-l1-context.png)

Frontend ini adalah komponen yang dilabel "Vercel Frontend" pada diagram. Ia menerima request dari aktor tenaga kesehatan, masyarakat, dan admin lewat browser, lalu meneruskan ke backend Flask di Cloud Run.

### Diagram C4 Level 2 (Container)

![C4 Level 2 Container: container Next.js (Vercel) memproksi ke container Flask (Cloud Run) yang membaca-tulis container GCS dan memanggil container openFDA eksternal](https://raw.githubusercontent.com/Bisura16/medWatch/main/docs/diagrams/png/c4-l2-container.png)

Container Next.js dijalankan di Vercel Hobby tier sebagai serverless function untuk API routes dan Edge Function untuk middleware. Pola proxy ini (Security Pattern B) didokumentasikan di [ADR-001](https://github.com/Bisura16/medWatch/blob/main/docs/adr/0001-vercel-cloud-run-security-pattern.md).

### Diagram Deployment

![Deployment diagram: browser klien terkoneksi ke Vercel CDN edge, lalu Vercel function memanggil Cloud Run service di asia-southeast1 yang mengakses GCS bucket dan Secret Manager](https://raw.githubusercontent.com/Bisura16/medWatch/main/docs/diagrams/png/deployment.png)

Frontend di-deploy ke `medwatch-frontend.vercel.app`. Variabel `BACKEND_API_URL` di-set lewat Vercel project settings (server-side scope saja). Backend di-deploy ke Cloud Run region `asia-southeast1`. Detail lengkap di [INSTALL.md](https://github.com/Bisura16/medWatch/blob/main/docs/INSTALL.md).

### Diagram alur sequence (Login)

![Sequence diagram login: browser POST credentials ke Vercel API route, route forward ke Flask login, Flask verifikasi bcrypt dan terbitkan JWT, route set httpOnly cookie](https://raw.githubusercontent.com/Bisura16/medWatch/main/docs/diagrams/png/seq-login.png)

Daftar lengkap diagram (use case, class, activity, state machine, ERD Chen, ERD Crow's Foot, sequence safety check, sequence PDF, sequence scraping) tersedia di repo backend pada folder [`docs/diagrams/png/`](https://github.com/Bisura16/medWatch/tree/main/docs/diagrams/png).

---

## 6. Prasyarat

- Node.js 22 LTS direkomendasikan. Node.js 25 baru saja dirilis dan menghasilkan warning kompatibilitas (`B-WAVE1-BUILD-1`), namun build dan dev server tetap berjalan. Detail mitigasi ada di [AS-BUILT.md Known Issues](https://github.com/Bisura16/medWatch/blob/main/docs/AS-BUILT.md).
- npm 10+.
- Akses ke backend (local Flask di port 8080 atau Cloud Run URL).
- Git 2.40+.

---

## 7. Instalasi

```bash
# 1. Clone repo
git clone https://github.com/Finerium/FrontendMedwatch.git
cd FrontendMedwatch

# 2. Install dependencies
npm install

# 3. Set environment variable
echo "BACKEND_API_URL=http://localhost:8080" > .env.local
# atau arahkan ke production:
# echo "BACKEND_API_URL=https://medwatch-api-517694123086.asia-southeast1.run.app" > .env.local

# 4. Jalankan dev server
npm run dev
# Buka http://localhost:3000
```

Panduan instalasi lengkap (termasuk setup backend secara lokal sebagai mitra) ada di [INSTALL.md backend](https://github.com/Bisura16/medWatch/blob/main/docs/INSTALL.md).

---

## 8. Konfigurasi

Variabel environment yang dibaca oleh frontend. Tidak ada nilai kredensial pernah dicommit ke repo.

| Nama | Wajib | Scope | Kegunaan |
|---|---|---|---|
| `BACKEND_API_URL` | ya | server-side saja | URL backend Cloud Run atau local. Tidak prefix `NEXT_PUBLIC_` sehingga tidak terexpose ke browser. |

Tidak ada secret yang disimpan di repo. Setting Vercel project di dashboard mengelola variabel ini per-environment (Production, Preview, Development). Postur keamanan menyeluruh dijelaskan di [SECURITY.md backend](https://github.com/Bisura16/medWatch/blob/main/docs/SECURITY.md).

---

## 9. Penggunaan

### Demo credentials

Klik tab pada `/login` untuk melihat preset demo per peran. Referensi cepat:

| Peran | Username | Password |
|---|---|---|
| Admin | `admin_ghaisan` | `admin2026` |
| Tenaga Kesehatan | `bidan_siti` | `siti2026` |
| Masyarakat | `umum_budi` | `budi2026` |

### Routes utama

| Route | Peran | Kegunaan |
|---|---|---|
| `/login` | public | Tiga tab login dengan demo creds |
| `/` (dashboard) | tenaga_kesehatan, admin | Dashboard KPI dengan grafik |
| `/patients` | tenaga_kesehatan, admin | Daftar pasien SOAP terurut newest-first |
| `/patients/new` | tenaga_kesehatan, admin | Form bidan-style dengan validasi range |
| `/patients/[id]` | tenaga_kesehatan, admin, owner | Detail printable |
| `/drug-search` | semua auth | Pencarian obat dengan alias |
| `/drug-compare` | semua auth | Perbandingan side-by-side |
| `/safety-checker` | semua auth | Cek interaksi multi-obat plus obat aktif pasien |
| `/visualization` | tenaga_kesehatan, admin | Tiga chart view dari API |
| `/heatmap` | semua auth | Heatmap obat x efek samping |
| `/export-pdf` | tenaga_kesehatan, admin | Empat tipe laporan PDF |
| `/admin/dashboard` | admin | Ringkasan sistem |
| `/admin/scraper` | admin | Trigger scraper (mocked) |
| `/admin/users` | admin | Manajemen akun pengguna |
| `/pasien/profile` | masyarakat | Profil self-service |
| `/_archived/*` | none | Halaman showcase awal yang sudah tidak diwire |

Daftar 30+ endpoint backend yang dipakai frontend ada di [API.md backend](https://github.com/Bisura16/medWatch/blob/main/docs/API.md).

---

## 10. Sumber Data dan Teknis Scraping

Data efek samping dan recall obat yang muncul di `/safety-checker`, `/heatmap`, `/drug-search`, dan ekspor PDF laporan efek samping berasal dari endpoint backend `/api/drugs/...` dan `/api/visualizations/...`. Backend pada gilirannya membaca file JSON yang dihasilkan oleh pipeline akuisisi openFDA.

### Riwayat sumber data

1. **Versi awal (Maret 2026):** modul `anggota1` (milik Ghaisan) melakukan scraping HTML dari `https://www.drugs.com/sfx/<obat>-side-effects.html` dan `https://www.drugs.com/fda-recalls/`.
2. **Mei 2026:** drugs.com bermigrasi ke proteksi Akamai edge dengan TLS fingerprinting yang memblokir setiap request dari script Python standar dengan HTTP 403 Forbidden. Kutipan langsung dari `anggota1/scraper.log` di repo backend:

   ```
   [1/2] scraping efek samping (64 obat)
     [1/64] ibuprofen
       status 403
     [2/64] paracetamol
       status 403
     [3/64] aspirin
       status 403
   ```

   64 dari 64 URL yang dicoba semua mengembalikan 403. Tidak ada bypass anti-bot yang dilakukan.
3. **Wave 1 (Mei 2026):** modul aditif `anggota1/openfda/` dibuat. Modul ini memakai openFDA REST API.

Decision lengkap ada di [ADR-004 backend](https://github.com/Bisura16/medWatch/blob/main/docs/adr/0004-drugs-com-akamai-to-openfda-pivot.md).

### Endpoint openFDA yang digunakan oleh pipeline backend

| Endpoint | Kegunaan |
|---|---|
| `https://api.fda.gov/drug/event.json` | FDA Adverse Event Reporting System (FAERS). |
| `https://api.fda.gov/drug/enforcement.json` | FDA Recall / Enforcement Reports. |

### Dasar legal

openFDA adalah layanan publik gratis yang dioperasikan oleh U.S. Food and Drug Administration. Konsumsi programmatic dengan API key diizinkan untuk penelitian, integrasi sistem informasi kesehatan, dan publikasi (Terms of Service: https://open.fda.gov/license/). Data FAERS dan Enforcement Reports tidak mengandung PII pasien; FDA sudah melakukan de-identifikasi sebelum dipublikasikan.

### Rate-limit handling

- Tanpa API key: 1.000 request / 24 jam per IP, 240 / menit.
- Dengan API key: 120.000 request / 24 jam per IP, 240 / menit.
- Polite delay 250 ms antar request, exponential backoff dengan jitter pada HTTP 429 dan 5xx (maksimum 5 retry).
- Frontend tidak pernah memegang atau menyentuh nilai `OPENFDA_API_KEY`. Key hanya ada di env backend Cloud Run.

### Cara regenerasi data

Regenerasi dilakukan di backend repo:

```bash
cd /path/to/medWatch
export OPENFDA_API_KEY=<your-key-here>
.venv/bin/python -m anggota1.openfda.fetch --max-recall-pages 6
```

### Hasil yang dicapai

Run Wave 1 pada 18 Mei 2026: **1.850 reaction-term occurrences** terdistribusi pada **74 baris adverse event** plus **6.000 baris recall**. Hasil ini terlihat di frontend lewat `/heatmap`, `/safety-checker`, dan ekspor PDF efek samping.

---

## 11. CRUD dan Data Model

Frontend memetakan tipe TypeScript ke skema kanonikal yang ditetapkan backend. Sumber kebenaran skema ada di [DATA-DICTIONARY.md backend](https://github.com/Bisura16/medWatch/blob/main/docs/DATA-DICTIONARY.md). Daftar endpoint lengkap dengan request/response shape ada di [API.md backend](https://github.com/Bisura16/medWatch/blob/main/docs/API.md).

### Patient SOAP schema (TypeScript di [`src/lib/patient-format.ts`](./src/lib/patient-format.ts))

```typescript
type Patient = {
  id: string;                  // P001 format
  tanggal_kunjungan?: string;  // DD-MM-YYYY
  nama: string;                // wajib
  umur?: string;
  alamat?: string;
  kategori?: string;           // Ibu Hamil, KB, Anak, Imunisasi, Umum, ...
  S: { keluhan: string; riwayat?: string };
  O: {
    tekanan_darah?: string;
    nadi?: string;
    suhu_c?: string;
    respirasi?: string;
    bb_kg?: string;
    tb_cm?: string;
    lila_cm?: string;
    catatan?: string;
  };
  A: { diagnosa: string };
  P: { tindakan: string; resep?: string; jadwal_kontrol?: string };
};
```

Detail view me-render skema ini dalam format bidan-style menggunakan helper `composeO()` dari `src/lib/patient-format.ts`. Field `O` yang kosong di-skip, abbreviation yang dipakai cocok dengan rekam tulisan tangan bidan (`td.`, `BB`, `tb`, `lila`).

### Visualisasi ERD

![ERD Crow's Foot menampilkan relasi User, Patient, Visit, Drug, Recall, AdverseEvent dengan kardinalitas](https://raw.githubusercontent.com/Bisura16/medWatch/main/docs/diagrams/png/erd-crowsfoot.png)

---

## 12. Struktur Proyek

```
FrontendMedwatch/
├── src/
│   ├── app/
│   │   ├── api/[...slug]/route.ts    # legacy proxy route (Next 15 era)
│   │   ├── login/page.tsx             # multi-role login
│   │   ├── admin/                     # admin-only pages
│   │   ├── pasien/                    # masyarakat-only pages
│   │   ├── patients/                  # SOAP CRUD pages
│   │   ├── safety-checker/page.tsx    # multi-drug safety analysis
│   │   ├── heatmap/page.tsx           # continuous color heatmap
│   │   ├── visualization/page.tsx     # chart trio
│   │   ├── drug-search/page.tsx       # autocomplete
│   │   ├── drug-compare/page.tsx      # side-by-side compare
│   │   ├── export-pdf/page.tsx        # 4 jenis laporan
│   │   └── _archived/                 # halaman showcase awal yang sudah tidak di-wire
│   ├── components/                    # UI components (layout, charts, ui)
│   ├── lib/
│   │   ├── api.ts                     # fetch wrapper
│   │   ├── auth-store.ts              # Zustand auth store
│   │   ├── store.ts                   # Zustand patient store (API-backed)
│   │   ├── patient-format.ts          # SOAP type + composeO helper
│   │   ├── patient-validation.ts      # range klinis untuk field numerik
│   │   ├── safety-checker.ts          # API wrapper
│   │   ├── pdf-generator.ts           # API wrapper (download blob)
│   │   └── heatmap-colors.ts          # d3-scale continuous 5-stop
│   ├── data/                          # data statis kategori, dll
│   ├── hooks/                         # custom React hooks
│   └── proxy.ts                       # Next 16 middleware ekuivalen
├── public/
│   └── indonesia-provinces.json       # topojson untuk archived map
├── screenshots/                       # bukti verifikasi Wave 1
├── docs/
│   ├── DESIGN_SYSTEM.md
│   └── MOCK_DATA.md
├── pitch-video/                       # Remotion video pitch (optional)
├── package.json
├── tsconfig.json
├── next.config.ts
└── README.md                          # file ini
```

Output sederhana dari `tree -L 2 -I 'node_modules|.next|.venv|__pycache__'` di repo root.

---

## 13. Testing

### Verifikasi visual

Folder [`screenshots/`](./screenshots/) berisi bukti uji visual dari Wave 1 (verifikasi B01-B11). Format: `<test-id>-<halaman>.png` plus dokumen pendukung PDF dan YAML snapshot.

### Test plan lengkap

Rencana pengujian formal black-box dengan teknik Equivalence Partitioning, Boundary Value Analysis, dan Decision Table mengikuti standar IEEE 829 akan diselesaikan di Wave 5 mission. Test plan dan Test Case TC-MOD-NNN akan didistribusikan attribusinya ke seluruh anggota tim dengan NIM.

---

## 14. Deployment

Frontend dideploy ke Vercel Hobby tier lewat repo `Finerium/FrontendMedwatch` di branch `main`. Push ke `main` memicu deployment otomatis. Setup environment variable `BACKEND_API_URL` dilakukan via Vercel dashboard atau CLI:

```bash
vercel --prod
```

Panduan lengkap (termasuk konfigurasi domain, environment per-stage, dan strategi rollback) ada di [INSTALL.md backend](https://github.com/Bisura16/medWatch/blob/main/docs/INSTALL.md) bagian Deploy.

---

## 15. Kontribusi Tim

Bagian ini menyimpan konten awal yang diauthor Ghaisan pada README versi sebelum Wave 2. Konten di-restructure ke section industri-standar di atas, namun tetap dipreserve di sini sebagai bukti kepemilikan dan riwayat kontribusi.

### Authorship awal (oleh Ghaisan Khoirul Badruzaman)

Frontend ini di-author oleh Ghaisan Khoirul Badruzaman sebagai bagian dari MedWatch integration. State terintegrasi tinggal di branch `ghaisan-APIIntegration`. Riwayat commit original showcase (premium glassmorphism showcase, fitur localStorage) dipertahankan.

### Frontend-Backend correlation pattern (oleh Ghaisan)

Frontend tidak pernah berbicara langsung dengan Cloud Run. Semua `/api/...` call dirutekan via [`src/proxy.ts`](./src/proxy.ts) sebagai Vercel proxy yang:

1. Forward request ke `BACKEND_API_URL` (server-only env var, tidak terexpose ke browser).
2. Attach JWT dari cookie httpOnly `medwatch_token` sebagai header `Authorization: Bearer ...`.
3. Pada `/api/auth/login`, set cookie dari field `token` di response backend.
4. Pada `/api/auth/logout`, hapus cookie.

Middleware auth me-redirect pengguna yang tidak terautentikasi ke `/login` dan menegakkan role-based access pada path `/admin/*` dan `/pasien/*`. Pola ini disebut Security Pattern B; alasan pemilihan ada di [ADR-001 backend](https://github.com/Bisura16/medWatch/blob/main/docs/adr/0001-vercel-cloud-run-security-pattern.md).

---

## 16. Cross-Link Repository

| Repo | Kegunaan | URL |
|---|---|---|
| Frontend (THIS repo) | Next.js 16 plus Tailwind v4 plus shadcn glassmorphism, dideploy ke Vercel | https://github.com/Finerium/FrontendMedwatch |
| Backend | Modul anggota1-5 plus integration layer Flask plus desktop CLI | https://github.com/Bisura16/medWatch |

README backend memiliki section detail tentang openFDA acquisition, ERD, struktur modul anggota1-5, dan ADR. Direkomendasikan dibaca berdampingan dengan README ini untuk gambaran lengkap sistem.

---

## 17. Lisensi

Lisensi MIT. Lihat [`LICENSE`](./LICENSE) untuk teks lengkap.
