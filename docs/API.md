---
title: API Reference MedWatch
version: 1.0.0
owner: Ghaisan Khoirul Badruzaman (251524048)
date: 2026-05-18
status: as-built
---

# API Reference MedWatch

Dokumen ini menjadi rujukan utama untuk setiap endpoint HTTP pada backend MedWatch. Seluruh klaim di sini diturunkan dari kode nyata di `api/` (Flask 3.x) dan proxy Next.js 15 pada `src/app/api/[...slug]/route.ts`. Jika ada perbedaan antara dokumen dan kode, kode dianggap sumber kebenaran dan dokumen ini perlu disinkronkan.

Penomoran sitasi memakai format `api/<file>.py:<line-start>-<line-end>` agar pembaca dapat menelusuri perilaku langsung di kode.

## 1. Pendahuluan

### 1.1 Posisi arsitektural

Backend MedWatch adalah aplikasi Flask yang dipublikasikan melalui dua jalur:

1. Akses langsung pada lokal pengembang via `gunicorn` atau `flask run`.
2. Akses via proxy Vercel Next.js 15 yang meneruskan ke Cloud Run. Browser hanya melihat domain Vercel; URL Cloud Run tersimpan pada env var `BACKEND_API_URL` yang server-only.

Lihat sitasi `api/app.py:27-66` untuk inisialisasi aplikasi dan registrasi blueprint, serta `src/app/api/[...slug]/route.ts:1-109` untuk proxy.

### 1.2 Base URL

| Konteks | URL | Catatan |
| --- | --- | --- |
| Pengembangan lokal langsung | `http://127.0.0.1:8080` | Default port di `api/config.py:36`. |
| Pengembangan lokal via proxy | `http://localhost:3000/api` | Proxy meneruskan ke `BACKEND_API_URL` sesuai env Vercel. |
| Produksi via Vercel | `https://medwatch-frontend.vercel.app/api` | Domain tetap Vercel; backend Cloud Run tersembunyi. |
| Produksi Cloud Run (resource name) | `medwatch-api` di proyek `medwatch-polban-2026`, region `asia-southeast1` | URL `*.run.app` tidak dipublikasikan ke browser. |

### 1.3 Cakupan dokumen

Semua endpoint pada blueprint berikut tercakup:

- `health.bp` lihat `api/routes/health.py:1-37`
- `auth_routes.bp` lihat `api/routes/auth_routes.py:1-52`
- `patient_routes.bp` lihat `api/routes/patient_routes.py:1-218`
- `drug_routes.bp` lihat `api/routes/drug_routes.py:1-52`
- `safety_routes.bp` lihat `api/routes/safety_routes.py:1-73`
- `visualization_routes.bp` lihat `api/routes/visualization_routes.py:1-139`
- `pdf_routes.bp` lihat `api/routes/pdf_routes.py:1-512`
- `admin_routes.bp` lihat `api/routes/admin_routes.py:1-128`

Pendaftaran blueprint dilakukan di `api/app.py:36-43`.

## 2. Konvensi

### 2.1 Format pertukaran

- Encoding payload: JSON, charset UTF-8.
- Header request yang relevan: `Content-Type: application/json` untuk metode POST/PUT, `Authorization: Bearer <jwt>` untuk endpoint terproteksi.
- Metode HTTP yang diizinkan oleh CORS: GET, POST, PUT, DELETE, OPTIONS. Lihat `api/app.py:30-34`.
- Header `Server` dihapus dari setiap response untuk mengurangi info bocoran. Lihat `api/app.py:58-61`.

### 2.2 Pembungkus response sukses dan error

Helper response standar didefinisikan di `api/helpers.py:6-13`:

- Sukses: payload dikembalikan apa adanya dengan status 200 atau 201. Jika tidak ada data, server mengembalikan `{ "status": "ok" }`.
- Error: payload berbentuk `{ "error": "<pesan>" }` dengan opsi `fields` ketika muncul kegagalan validasi multi-field. Status kode mengikuti semantik HTTP: 400 untuk validasi gagal, 401 untuk autentikasi gagal, 403 untuk pelanggaran role, 404 untuk resource tidak ditemukan, 409 untuk konflik, 503 untuk dependensi tidak tersedia.

Contoh response error generik:

```json
{
  "error": "missing or invalid token"
}
```

Contoh response error validasi multi-field (dipakai pada CRUD pasien, lihat `api/routes/patient_routes.py:175-178`):

```json
{
  "error": "Validasi gagal",
  "fields": [
    "BB (kg) harus berupa angka.",
    "Tekanan darah harus dalam format sistolik/diastolik (mis. 120/80)."
  ]
}
```

### 2.3 Status code

| Kode | Makna utama |
| --- | --- |
| 200 | Sukses, payload tersedia. |
| 201 | Resource dibuat. |
| 204 | Sukses tanpa body (delete). |
| 400 | Validasi gagal atau parameter wajib tidak ada. |
| 401 | Token absen atau invalid. |
| 403 | Token valid namun role tidak diizinkan. |
| 404 | Resource tidak ditemukan. |
| 409 | Konflik resource (mis. username sudah dipakai). |
| 500 | Galat internal. |
| 502 | Proxy Vercel tidak dapat menjangkau backend (`src/app/api/[...slug]/route.ts:20-25,52-58`). |
| 503 | Dependensi modul anggota tidak tersedia. |

### 2.4 Lokal, zona waktu, format

- Tanggal kunjungan pasien memakai format `DD-MM-YYYY` sesuai konvensi Bimo (`api/routes/patient_routes.py:30-45`).
- Timestamp sistem (mis. `time` pada `/api/health`, `process_started_at` pada `/api/admin/system-stats`) memakai ISO 8601 UTC dari `datetime.now(timezone.utc).isoformat()`.
- Stempel waktu footer PDF memakai WIB UTC+7 (`api/routes/pdf_routes.py:35-39`).

## 3. Autentikasi

### 3.1 Mekanisme

MedWatch memakai JWT yang diterbitkan oleh `POST /api/auth/login`. JWT berisi klaim `sub` (username), `role`, `name`, `iat`, `exp`, dan `iss = medwatch-api`. Algoritma tanda tangan HS256 dengan `JWT_SECRET` yang diambil dari env. Masa berlaku 12 jam. Lihat `api/auth.py:22-32`.

Verifikasi JWT membandingkan signature dan klaim `iss`. Token tidak valid mengembalikan `None`. Lihat `api/auth.py:35-39`.

Penyimpanan password memakai bcrypt dengan cost 12, dihitung oleh `api/auth.py:11-12`. Verifikasi password aman terhadap exception (`api/auth.py:15-19`).

### 3.2 Distribusi token ke klien

Dua jalur:

1. Akses langsung ke backend: klien menyimpan JWT sendiri dan mengirim header `Authorization: Bearer <jwt>` pada setiap request terproteksi (`api/middleware.py:10-14`).
2. Akses via proxy Vercel: proxy menyimpan JWT pada cookie `medwatch_token`. Properti cookie: `httpOnly`, `sameSite=lax`, `secure` saat production, `maxAge` 12 jam, `path=/` (`src/app/api/[...slug]/route.ts:13-14,76-93`). Proxy otomatis menyalin nilai cookie ke header `Authorization` saat meneruskan request ke backend (`src/app/api/[...slug]/route.ts:38-42`).

### 3.3 Decorator role

Decorator `require_auth` memastikan token valid lalu mengisi `g.user` (`api/middleware.py:17-34`). Decorator `require_role(*allowed)` adalah varian yang menolak request bila `g.user.role` tidak ada di daftar yang diperbolehkan (`api/middleware.py:37-51`).

### 3.4 Logout

`POST /api/auth/logout` di backend bersifat idempotent dan hanya membalas `{ "status": "logged_out" }` (`api/routes/auth_routes.py:49-51`). Pembersihan cookie sebenarnya terjadi pada proxy Vercel yang menulis cookie kosong dengan `maxAge=0` (`src/app/api/[...slug]/route.ts:95-103`).

## 4. RBAC Matrix

Tabel di bawah merangkum role yang diizinkan untuk setiap endpoint. Decorator `require_role` diturunkan dari kode masing-masing blueprint.

| Endpoint | tenaga_kesehatan | masyarakat | admin | Tanpa auth | Catatan |
| --- | --- | --- | --- | --- | --- |
| `GET /api/health` |  |  |  | ya | Public (`api/routes/health.py:12-18`). |
| `GET /api/info` |  |  |  | ya | Public (`api/routes/health.py:21-36`). |
| `POST /api/auth/login` |  |  |  | ya | Mengeluarkan token (`api/routes/auth_routes.py:13-40`). |
| `GET /api/auth/me` | ya | ya | ya |  | `require_auth` (`api/routes/auth_routes.py:43-46`). |
| `POST /api/auth/logout` |  |  |  | ya | Cookie cleared di proxy. |
| `GET /api/patients` | ya |  | ya |  | `require_role` (`api/routes/patient_routes.py:135-146`). |
| `GET /api/patients/<pid>` | ya | ya (kepemilikan) | ya |  | `masyarakat` hanya melihat record dengan `owner_username` cocok (`api/routes/patient_routes.py:149-159`). |
| `POST /api/patients` | ya |  | ya |  | (`api/routes/patient_routes.py:162-187`). |
| `PUT /api/patients/<pid>` | ya |  | ya |  | (`api/routes/patient_routes.py:190-205`). |
| `DELETE /api/patients/<pid>` |  |  | ya |  | (`api/routes/patient_routes.py:208-217`). |
| `GET /api/drugs` |  |  |  | ya | Public katalog (`api/routes/drug_routes.py:19-28`). |
| `GET /api/drugs/search` |  |  |  | ya | (`api/routes/drug_routes.py:31-40`). |
| `GET /api/drugs/<nama_obat>` |  |  |  | ya | (`api/routes/drug_routes.py:43-51`). |
| `POST /api/safety/check` | ya | ya | ya |  | `require_auth` (`api/routes/safety_routes.py:16-72`). |
| `GET /api/visualizations/kunjungan-trend` | ya |  | ya |  | (`api/routes/visualization_routes.py:54-66`). |
| `GET /api/visualizations/keluhan-distribution` | ya |  | ya |  | (`api/routes/visualization_routes.py:69-80`). |
| `GET /api/visualizations/top-efek-samping` | ya | ya | ya |  | `require_auth` (`api/routes/visualization_routes.py:83-110`). |
| `GET /api/visualizations/heatmap-efek` | ya | ya | ya |  | `require_auth` (`api/routes/visualization_routes.py:113-138`). |
| `POST /api/pdf/generate-rekam-medis` | ya |  | ya |  | (`api/routes/pdf_routes.py:169-202`). |
| `POST /api/pdf/generate-laporan-bulanan` |  |  | ya |  | (`api/routes/pdf_routes.py:205-238`). |
| `POST /api/pdf/generate-efek-samping` | ya |  | ya |  | (`api/routes/pdf_routes.py:241-385`). |
| `POST /api/pdf/generate-inventaris` | ya |  | ya |  | (`api/routes/pdf_routes.py:388-511`). |
| `POST /api/admin/scrape` |  |  | ya |  | (`api/routes/admin_routes.py:21-38`). |
| `GET /api/admin/users` |  |  | ya |  | (`api/routes/admin_routes.py:41-45`). |
| `POST /api/admin/users` |  |  | ya |  | (`api/routes/admin_routes.py:48-85`). |
| `DELETE /api/admin/users/<username>` |  |  | ya |  | Tidak boleh menghapus admin terakhir (`api/routes/admin_routes.py:88-103`). |
| `GET /api/admin/system-stats` |  |  | ya |  | (`api/routes/admin_routes.py:106-127`). |

Catatan: kolom kosong berarti role tersebut akan menerima 401 (tidak login) atau 403 (login namun role salah).

## 5. Referensi Endpoint

### 5.1 Health blueprint

#### 5.1.1 GET /api/health

- Method dan path: `GET /api/health`.
- Auth: tidak ada.
- Query: tidak ada.
- Body: tidak ada.
- Response 200:

```json
{
  "status": "ok",
  "version": "1.0.0",
  "time": "2026-05-18T08:00:00+00:00"
}
```

- Error: tidak ada jalur error spesifik.
- Source: `api/routes/health.py:12-18`.

#### 5.1.2 GET /api/info

- Method dan path: `GET /api/info`.
- Auth: tidak ada.
- Query: tidak ada.
- Body: tidak ada.
- Response 200:

```json
{
  "modules_loaded": {
    "anggota2.pasien_helper": true,
    "anggota4.data_loader": true,
    "anggota4.safety_checker": true,
    "anggota4.pencarian_obat": true,
    "anggota5.export_pdf": true
  },
  "cloud_storage": false,
  "project": "medwatch-polban-2026"
}
```

- Error: tidak ada jalur error spesifik.
- Source: `api/routes/health.py:21-36`.

### 5.2 Auth blueprint

#### 5.2.1 POST /api/auth/login

- Method dan path: `POST /api/auth/login`.
- Auth: tidak ada.
- Body schema:

| Field | Tipe | Wajib | Catatan |
| --- | --- | --- | --- |
| `username` | string | ya | Spasi tepi di-trim oleh server. |
| `password` | string | ya | Tidak pernah di-log oleh backend. |

- Response 200:

```json
{
  "token": "eyJ.<jwt-redacted>",
  "user": {
    "username": "bidan-demo",
    "role": "tenaga_kesehatan",
    "name": "Bidan Demo"
  }
}
```

- Error 401:

```json
{ "error": "invalid credentials" }
```

- Source: `api/routes/auth_routes.py:13-40`.
- Catatan proxy: bila login sukses, proxy Vercel menambahkan cookie `medwatch_token` (`src/app/api/[...slug]/route.ts:76-93`).

#### 5.2.2 GET /api/auth/me

- Method dan path: `GET /api/auth/me`.
- Auth: Bearer JWT.
- Query: tidak ada.
- Response 200:

```json
{
  "username": "bidan-demo",
  "role": "tenaga_kesehatan",
  "name": "Bidan Demo"
}
```

- Error 401:

```json
{ "error": "missing or invalid token" }
```

- Source: `api/routes/auth_routes.py:43-46`.

#### 5.2.3 POST /api/auth/logout

- Method dan path: `POST /api/auth/logout`.
- Auth: tidak ada (idempotent).
- Body: kosong.
- Response 200:

```json
{ "status": "logged_out" }
```

- Source: `api/routes/auth_routes.py:49-51`.
- Catatan proxy: cookie `medwatch_token` dihapus oleh proxy Vercel (`src/app/api/[...slug]/route.ts:95-103`).

### 5.3 Patient blueprint

Skema entitas pasien (Bimo) selengkapnya dijelaskan pada `docs/DATA-DICTIONARY.md`. Bagian ini hanya menampilkan field yang relevan dengan endpoint.

#### 5.3.1 GET /api/patients

- Method dan path: `GET /api/patients`.
- Auth: role `tenaga_kesehatan` atau `admin`.
- Query: tidak ada.
- Response 200 (urut tanggal kunjungan menurun, tiebreak by id menurun, lihat Iterasi 1 T1-PASIEN):

```json
[
  {
    "id": "P003",
    "nama": "Ny. Aminah",
    "umur": 30,
    "tanggal_kunjungan": "10-05-2026",
    "kategori": "Ibu Hamil"
  },
  {
    "id": "P002",
    "nama": "An. Budi",
    "umur": 5,
    "tanggal_kunjungan": "10-05-2026",
    "kategori": "Anak"
  }
]
```

- Error 401 atau 403 sesuai role.
- Source: `api/routes/patient_routes.py:135-146` dan helper sort `api/routes/patient_routes.py:30-53`.

#### 5.3.2 GET /api/patients/<pid>

- Method dan path: `GET /api/patients/<pid>`.
- Auth: `require_auth`. Role `masyarakat` hanya diizinkan bila `owner_username` cocok dengan klaim `sub`.
- Response 200: objek pasien lengkap dengan struktur SOAP.

```json
{
  "id": "P001",
  "nama": "Ny. Dewi",
  "umur": 25,
  "tanggal_kunjungan": "28-02-2026",
  "alamat": "Kp. Selang Cau",
  "kategori": "Ibu Hamil",
  "S": {
    "keluhan": "mual, muntah, pusing",
    "riwayat": "telat mens 1 bulan"
  },
  "O": {
    "tekanan_darah": "110/70",
    "bb_kg": 50,
    "tb_cm": 150,
    "lila_cm": 23,
    "catatan": "tespek positif"
  },
  "A": { "diagnosa": "G1P0A0 hamil 5 minggu" },
  "P": {
    "tindakan": "Istirahat cukup\nMakan sedikit tapi sering",
    "resep": "Asam folat 1x1 sehari",
    "jadwal_kontrol": "4 minggu lagi"
  }
}
```

- Error 404 atau 403.
- Source: `api/routes/patient_routes.py:149-159`.

#### 5.3.3 POST /api/patients

- Method dan path: `POST /api/patients`.
- Auth: role `tenaga_kesehatan` atau `admin`.
- Body schema (minimum):

| Field | Tipe | Wajib | Catatan |
| --- | --- | --- | --- |
| `nama` | string | ya | (`api/routes/patient_routes.py:166-167`). |
| `S.keluhan` | string | ya | |
| `A.diagnosa` | string | ya | |
| `P.tindakan` | string | ya | |
| `tanggal_kunjungan` | string `DD-MM-YYYY` | tidak | |
| `umur` | integer | tidak | |
| `alamat` | string | tidak | |
| `kategori` | string | tidak | |
| `O.tekanan_darah` | string `sistolik/diastolik` | tidak | Divalidasi 60..250 / 30..160. |
| `O.bb_kg` | numerik 1..300 | tidak | |
| `O.tb_cm` | numerik 30..300 | tidak | |
| `O.lila_cm` | numerik 8..60 | tidak | |
| `O.nadi` | numerik 30..220 | tidak | |
| `O.suhu_c` | numerik 30..44 | tidak | |
| `O.respirasi` | numerik 5..80 | tidak | |

- Response 201: objek pasien yang sudah disimpan, mengandung `id` (`P###`) dan `created_by` (username pembuat).
- Error 400 generik:

```json
{ "error": "nama required" }
```

- Error 400 validasi multi-field (Iterasi 1 T1-PASIEN B03):

```json
{
  "error": "Validasi gagal",
  "fields": [
    "BB (kg) harus antara 1 dan 300.",
    "Tekanan darah harus dalam format sistolik/diastolik (mis. 120/80)."
  ]
}
```

- Source: `api/routes/patient_routes.py:162-187`. Aturan validasi numerik `api/routes/patient_routes.py:17-99`.

#### 5.3.4 PUT /api/patients/<pid>

- Method dan path: `PUT /api/patients/<pid>`.
- Auth: role `tenaga_kesehatan` atau `admin`.
- Body: parsial. Server melakukan deep-merge ke dokumen eksisting (`api/routes/patient_routes.py:125-132,198-202`).
- Validasi: validasi rentang numerik berjalan sama dengan POST (Iterasi 1 T1-PASIEN). 400 dengan `fields: [...]` bila gagal.
- Response 200: objek pasien hasil merge.
- Error 404: bila `pid` tidak ditemukan.
- Source: `api/routes/patient_routes.py:190-205`.

#### 5.3.5 DELETE /api/patients/<pid>

- Method dan path: `DELETE /api/patients/<pid>`.
- Auth: role `admin` saja.
- Response 204: body kosong.
- Error 404:

```json
{ "error": "not found" }
```

- Source: `api/routes/patient_routes.py:208-217`.

### 5.4 Drug blueprint

#### 5.4.1 GET /api/drugs

- Method dan path: `GET /api/drugs`.
- Auth: tidak ada.
- Query:

| Param | Tipe | Wajib | Catatan |
| --- | --- | --- | --- |
| `category` | string | tidak | Case-insensitive filter pada field `kategori` obat. |

- Response 200: array objek obat sesuai skema `anggota4/data/drug_database.json`. Contoh ringkas:

```json
[
  {
    "nama_obat": "Paracetamol",
    "alias": ["Acetaminophen"],
    "kategori": "Analgesik",
    "bahan_aktif": ["Paracetamol"],
    "indikasi": ["nyeri ringan", "demam"],
    "dosis_umum": "500 mg setiap 4-6 jam",
    "kehamilan": "Kategori B",
    "peringatan": ["hindari pada gangguan hati berat"],
    "kontraindikasi": ["hipersensitivitas paracetamol"],
    "interaksi": ["warfarin"],
    "efek_samping": ["mual", "ruam"]
  }
]
```

- Error 503:

```json
{ "error": "drug catalog unavailable" }
```

- Source: `api/routes/drug_routes.py:19-28`.

#### 5.4.2 GET /api/drugs/search

- Method dan path: `GET /api/drugs/search`.
- Auth: tidak ada.
- Query:

| Param | Tipe | Wajib | Catatan |
| --- | --- | --- | --- |
| `q` | string | ya | Bila kosong, response 200 dengan array kosong. |

- Response 200: array hasil dari `anggota4.pencarian_obat.cari_obat(q)["hasil"]`.

```json
[
  { "nama_obat": "Paracetamol", "match_score": 0.95 }
]
```

- Error 503:

```json
{ "error": "search unavailable" }
```

- Source: `api/routes/drug_routes.py:31-40`.

#### 5.4.3 GET /api/drugs/<nama_obat>

- Method dan path: `GET /api/drugs/<nama_obat>`.
- Auth: tidak ada.
- Response 200: profil keamanan lengkap dari `anggota4.pencarian_obat.ambil_profil_keamanan_lengkap` selama field `status` bernilai `found`.
- Error 404:

```json
{ "error": "not found" }
```

- Error 503:

```json
{ "error": "drug profile unavailable" }
```

- Source: `api/routes/drug_routes.py:43-51`.

### 5.5 Safety blueprint

#### 5.5.1 POST /api/safety/check

- Method dan path: `POST /api/safety/check`.
- Auth: `require_auth`.
- Body schema:

| Field | Tipe | Wajib | Catatan |
| --- | --- | --- | --- |
| `drugs` | array string | ya | Minimal 1 elemen. |
| `pasien_id` | string | tidak | Bila diisi, server memuat record pasien dan mengisi konteks tambahan. |

- Response 200 (Iterasi 1 T1-SAFETY menambah field `pasien_active_meds`):

```json
{
  "drugs": [
    {
      "nama_obat": "Paracetamol",
      "label_risiko": "rendah",
      "skor_risiko": 1,
      "efek_samping": ["mual"]
    }
  ],
  "interactions": [],
  "severity_score": 1,
  "severity_level": "low",
  "warnings": [],
  "obat_tidak_ditemukan": [],
  "pasien_context": {
    "id": "P001",
    "nama": "Ny. Dewi",
    "kategori": "Ibu Hamil",
    "diagnosa": "G1P0A0 hamil 5 minggu",
    "kondisi_umum": "telat mens 1 bulan"
  },
  "pasien_active_meds": ["Asam folat"]
}
```

- Field `severity_level` adalah mapping ke nilai bahasa Inggris (`rendah->low`, `sedang->medium`, `tinggi->high`) untuk konsumsi UI. Lihat `api/routes/safety_routes.py:12-14,33-38,67`.
- Field `pasien_active_meds` di-parse dari `P.resep` pasien menggunakan `helpers.parse_resep_to_meds` (`api/helpers.py:47-96`). Bila `pasien_id` tidak diisi atau pasien tidak ditemukan, field tetap dikembalikan sebagai array kosong `[]`.
- Error 400:

```json
{ "error": "drugs (non-empty list) required" }
```

- Error 503:

```json
{ "error": "safety checker unavailable" }
```

- Source: `api/routes/safety_routes.py:16-72`.

### 5.6 Visualization blueprint

#### 5.6.1 GET /api/visualizations/kunjungan-trend

- Method dan path: `GET /api/visualizations/kunjungan-trend`.
- Auth: role `tenaga_kesehatan` atau `admin`.
- Response 200: array 12 bulan dengan label Indonesia singkat.

```json
[
  { "month": "Jan", "count": 12 },
  { "month": "Feb", "count": 18 },
  { "month": "Mar", "count": 25 }
]
```

- Source: `api/routes/visualization_routes.py:54-66`. Bila tidak ada data pasien, server membalas data dummy demonstrasi (`api/routes/visualization_routes.py:38-41`).

#### 5.6.2 GET /api/visualizations/keluhan-distribution

- Method dan path: `GET /api/visualizations/keluhan-distribution`.
- Auth: role `tenaga_kesehatan` atau `admin`.
- Response 200:

```json
[
  { "kategori": "Ibu Hamil", "count": 28 },
  { "kategori": "Anak", "count": 18 }
]
```

- Source: `api/routes/visualization_routes.py:69-80`.

#### 5.6.3 GET /api/visualizations/top-efek-samping

- Method dan path: `GET /api/visualizations/top-efek-samping`.
- Auth: `require_auth`.
- Response 200: top 10 efek samping berdasarkan kemunculan pada katalog obat.

```json
[
  {
    "nama_efek": "Mual",
    "count": 12,
    "kategori": "Gastrointestinal",
    "tingkat_keparahan": "ringan"
  }
]
```

- Source: `api/routes/visualization_routes.py:83-110`.

#### 5.6.4 GET /api/visualizations/heatmap-efek

- Method dan path: `GET /api/visualizations/heatmap-efek`.
- Auth: `require_auth`.
- Response 200: matriks biner drug x effect.

```json
{
  "drugs": ["Paracetamol", "Amoxicillin"],
  "effects": ["mual", "ruam"],
  "values": [
    [1, 1],
    [1, 0]
  ]
}
```

- Source: `api/routes/visualization_routes.py:113-138`.

### 5.7 PDF blueprint

Semua endpoint PDF mengembalikan response `application/pdf` sebagai attachment via `flask.send_file`. Nama file unduhan ditentukan parameter `download_name`.

#### 5.7.1 POST /api/pdf/generate-rekam-medis

- Method dan path: `POST /api/pdf/generate-rekam-medis`.
- Auth: role `tenaga_kesehatan` atau `admin`.
- Body schema:

| Field | Tipe | Wajib |
| --- | --- | --- |
| `pasien_id` | string | ya |

- Response 200: file PDF rekam medis pasien tunggal. Nama unduhan `rekam-medis-<pasien_id>.pdf`.
- Error 400:

```json
{ "error": "pasien_id required" }
```

- Error 404 bila pasien tidak ditemukan, 503 bila modul `anggota5.export_pdf` belum termuat, 500 bila generator melempar exception.
- Source: `api/routes/pdf_routes.py:169-202`.

#### 5.7.2 POST /api/pdf/generate-laporan-bulanan

- Method dan path: `POST /api/pdf/generate-laporan-bulanan`.
- Auth: role `admin` saja.
- Body schema:

| Field | Tipe | Wajib | Catatan |
| --- | --- | --- | --- |
| `month` | string `YYYY-MM` | tidak | Bila kosong, semua pasien diikutkan. |

- Response 200: file PDF agregat. Nama unduhan `laporan-bulanan-<month-or-semua>.pdf`.
- Error 503 atau 500 sesuai jalur kegagalan modul.
- Source: `api/routes/pdf_routes.py:205-238`.

#### 5.7.3 POST /api/pdf/generate-efek-samping (Iterasi 1 T1-PDF)

- Method dan path: `POST /api/pdf/generate-efek-samping`.
- Auth: role `tenaga_kesehatan` atau `admin`.
- Body: kosong (server membaca seluruh data pasien dan basis data obat).
- Response 200: PDF berisi ringkasan, tabel top 25 efek samping, tabel severitas per obat, dan catatan metodologi pembobotan.
- Error 503:

```json
{ "error": "data efek samping tidak tersedia" }
```

- Error 500 bila generator melempar exception.
- Source: `api/routes/pdf_routes.py:241-385`. Helper severity `api/routes/pdf_routes.py:108-112`. Parser resep `api/routes/pdf_routes.py:115-132`.

#### 5.7.4 POST /api/pdf/generate-inventaris (Iterasi 1 T1-PDF)

- Method dan path: `POST /api/pdf/generate-inventaris`.
- Auth: role `tenaga_kesehatan` atau `admin`.
- Body: kosong.
- Response 200: PDF inventaris katalog obat (sumber `anggota4/data/drug_database.json`).
- Error 503 bila data katalog tidak tersedia, 500 untuk galat generator.
- Source: `api/routes/pdf_routes.py:388-511`.

### 5.8 Admin blueprint

#### 5.8.1 POST /api/admin/scrape

- Method dan path: `POST /api/admin/scrape`.
- Auth: role `admin`.
- Body: kosong.
- Response 200:

```json
{
  "status": "completed",
  "drugs_updated": 25,
  "recalls_added": 0,
  "source": "cached",
  "timestamp": "2026-05-18T08:30:00+00:00"
}
```

- Source: `api/routes/admin_routes.py:21-38`. Catatan: jalur ini bersifat mock untuk demo. Pemicu asli `anggota1` di-jalankan di luar request HTTP.

#### 5.8.2 GET /api/admin/users

- Method dan path: `GET /api/admin/users`.
- Auth: role `admin`.
- Response 200: array user tanpa field password (`api/helpers.py:16-18`).

```json
[
  {
    "username": "admin-demo",
    "role": "admin",
    "name": "Admin Demo",
    "phone": "0812xxxxxxx"
  }
]
```

- Source: `api/routes/admin_routes.py:41-45`.

#### 5.8.3 POST /api/admin/users

- Method dan path: `POST /api/admin/users`.
- Auth: role `admin`.
- Body schema:

| Field | Tipe | Wajib | Catatan |
| --- | --- | --- | --- |
| `username` | string | tidak | Bila kosong, server menyusun dari `name` + 4 digit terakhir `phone`. |
| `password` | string | ya | Disimpan sebagai bcrypt hash. |
| `role` | string | ya | Harus salah satu dari `tenaga_kesehatan`, `masyarakat`, `admin`. |
| `name` | string | tidak | |
| `phone` | string | tidak | |

- Response 201: representasi user tanpa password (`api/helpers.py:16-18`).
- Error 400:

```json
{ "error": "password required" }
```

- Error 409:

```json
{ "error": "username exists" }
```

- Source: `api/routes/admin_routes.py:48-85`.

#### 5.8.4 DELETE /api/admin/users/<username>

- Method dan path: `DELETE /api/admin/users/<username>`.
- Auth: role `admin`.
- Response 204: kosong.
- Error 404:

```json
{ "error": "not found" }
```

- Error 400:

```json
{ "error": "cannot delete last admin" }
```

- Source: `api/routes/admin_routes.py:88-103`.

#### 5.8.5 GET /api/admin/system-stats (Iterasi 1 T1-ADMIN)

- Method dan path: `GET /api/admin/system-stats`.
- Auth: role `admin`.
- Response 200 (field `process_started_at` dan `uptime_seconds` ditambahkan Iterasi 1 untuk menggantikan KPI hardcoded B10):

```json
{
  "users_count": 4,
  "patients_count": 12,
  "drugs_count": 25,
  "last_scrape": {
    "status": "completed",
    "drugs_updated": 25,
    "recalls_added": 0,
    "source": "cached",
    "timestamp": "2026-05-18T08:30:00+00:00"
  },
  "users_by_role": {
    "tenaga_kesehatan": 2,
    "masyarakat": 1,
    "admin": 1
  },
  "process_started_at": "2026-05-18T07:00:00+00:00",
  "uptime_seconds": 5400
}
```

- `last_scrape` bernilai `null` bila belum pernah ada scrape dalam siklus proses tersebut.
- Source: `api/routes/admin_routes.py:106-127`. Inisialisasi `_PROCESS_STARTED_AT` pada module import: `api/routes/admin_routes.py:17-18`.

## 6. Proxy Next.js

Proxy pada `src/app/api/[...slug]/route.ts` adalah satu-satunya jalur publik di production. Karakteristik utama:

- Method yang diteruskan: GET, POST, PUT, DELETE (`src/app/api/[...slug]/route.ts:108`).
- Header `host`, `cookie`, `connection` di-strip sebelum forward ke backend (`src/app/api/[...slug]/route.ts:31-37`).
- Cookie `medwatch_token` dibaca dan diubah menjadi header `Authorization: Bearer <token>` (`src/app/api/[...slug]/route.ts:38-42`).
- Body request diteruskan apa adanya kecuali untuk GET/HEAD (`src/app/api/[...slug]/route.ts:44-48`).
- Bila `BACKEND_API_URL` belum diset, proxy membalas 502 dengan body `{ "error": "BACKEND_API_URL not configured" }` (`src/app/api/[...slug]/route.ts:20-25`).
- Bila upstream tidak terjangkau, proxy membalas 502 dengan body `{ "error": "upstream unreachable", "detail": "<exception>" }` (`src/app/api/[...slug]/route.ts:52-58`).

## 7. Pengaruh Iterasi 1 pada API

Iterasi 1 menambah atau mengubah perilaku endpoint berikut:

| Endpoint | Perubahan | Sumber |
| --- | --- | --- |
| `POST /api/safety/check` | Tambah `pasien_active_meds` di response (T1-SAFETY). | `api/routes/safety_routes.py:44-72` |
| `GET /api/patients` | Urutan default tanggal kunjungan menurun, tiebreak by id menurun (T1-PASIEN B07). | `api/routes/patient_routes.py:135-146` |
| `POST /api/patients`, `PUT /api/patients/<pid>` | Validasi rentang numerik medis dengan jawaban 400 + `fields[]` (T1-PASIEN B03). | `api/routes/patient_routes.py:56-99,175-178,194-197` |
| `POST /api/pdf/generate-efek-samping` | Endpoint baru (T1-PDF B04). | `api/routes/pdf_routes.py:241-385` |
| `POST /api/pdf/generate-inventaris` | Endpoint baru (T1-PDF B04). | `api/routes/pdf_routes.py:388-511` |
| `GET /api/admin/system-stats` | Tambah `process_started_at` dan `uptime_seconds` real, hapus angka hardcoded (T1-ADMIN B10). | `api/routes/admin_routes.py:17-18,106-127` |

## 8. Lampiran OpenAPI 3.1

Spesifikasi di bawah hanya mendeskripsikan endpoint backend (bukan proxy). Skema autentikasi dideklarasikan via cookie `medwatch_token`. Contoh nilai pada deskripsi adalah placeholder pendek tanpa data nyata.

```yaml
openapi: 3.1.0
info:
  title: MedWatch API
  version: 1.0.0
  description: |
    Backend Flask untuk MedWatch (Faskes 1 Bidan).
    Akses produksi disarankan melalui proxy Vercel Next.js.
servers:
  - url: http://127.0.0.1:8080
    description: Local dev (gunicorn atau flask run)
  - url: http://localhost:3000/api
    description: Local dev via proxy Next.js
  - url: https://medwatch-frontend.vercel.app/api
    description: Production via proxy Vercel
components:
  securitySchemes:
    cookieAuth:
      type: apiKey
      in: cookie
      name: medwatch_token
      description: JWT (HS256) issued by POST /api/auth/login, stored as httpOnly cookie by the Vercel proxy.
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: Direct backend access uses Authorization Bearer header.
  schemas:
    Error:
      type: object
      required: [error]
      properties:
        error:
          type: string
        fields:
          type: array
          items:
            type: string
    User:
      type: object
      properties:
        username: { type: string }
        role:
          type: string
          enum: [tenaga_kesehatan, masyarakat, admin]
        name: { type: string }
        phone: { type: string }
    LoginRequest:
      type: object
      required: [username, password]
      properties:
        username: { type: string }
        password: { type: string, format: password }
    LoginResponse:
      type: object
      properties:
        token: { type: string }
        user: { $ref: "#/components/schemas/User" }
    PatientSummary:
      type: object
      properties:
        id: { type: string, pattern: "^P[0-9]{3}$" }
        nama: { type: string }
        umur: { type: integer }
        tanggal_kunjungan: { type: string, description: "DD-MM-YYYY" }
        kategori: { type: string }
    PatientS:
      type: object
      properties:
        keluhan: { type: string }
        riwayat: { type: string }
    PatientO:
      type: object
      properties:
        tekanan_darah: { type: string, description: "sistolik/diastolik" }
        nadi: { type: number }
        suhu_c: { type: number }
        respirasi: { type: number }
        bb_kg: { type: number }
        tb_cm: { type: number }
        lila_cm: { type: number }
        catatan: { type: string }
    PatientA:
      type: object
      properties:
        diagnosa: { type: string }
    PatientP:
      type: object
      properties:
        tindakan: { type: string }
        resep: { type: string }
        jadwal_kontrol: { type: string }
    Patient:
      type: object
      required: [nama]
      properties:
        id: { type: string, pattern: "^P[0-9]{3}$" }
        nama: { type: string }
        umur: { type: integer }
        tanggal_kunjungan: { type: string }
        alamat: { type: string }
        kategori: { type: string }
        owner_username: { type: string }
        created_by: { type: string }
        S: { $ref: "#/components/schemas/PatientS" }
        O: { $ref: "#/components/schemas/PatientO" }
        A: { $ref: "#/components/schemas/PatientA" }
        P: { $ref: "#/components/schemas/PatientP" }
    DrugCatalogEntry:
      type: object
      properties:
        nama_obat: { type: string }
        alias: { type: array, items: { type: string } }
        kategori: { type: string }
        bahan_aktif: { type: array, items: { type: string } }
        indikasi: { type: array, items: { type: string } }
        dosis_umum: { type: string }
        kehamilan: { type: string }
        peringatan: { type: array, items: { type: string } }
        kontraindikasi: { type: array, items: { type: string } }
        interaksi: { type: array, items: { type: string } }
        efek_samping: { type: array, items: { type: string } }
    SafetyCheckRequest:
      type: object
      required: [drugs]
      properties:
        drugs:
          type: array
          items: { type: string }
        pasien_id: { type: string }
    SafetyCheckResponse:
      type: object
      properties:
        drugs:
          type: array
          items:
            type: object
        interactions:
          type: array
          items:
            type: object
        severity_score: { type: integer }
        severity_level:
          type: string
          enum: [low, medium, high]
        warnings:
          type: array
          items: { type: string }
        obat_tidak_ditemukan:
          type: array
          items: { type: string }
        pasien_context:
          type: object
          nullable: true
        pasien_active_meds:
          type: array
          items: { type: string }
    KunjunganTrendPoint:
      type: object
      properties:
        month: { type: string }
        count: { type: integer }
    KeluhanDistributionPoint:
      type: object
      properties:
        kategori: { type: string }
        count: { type: integer }
    TopEfekSampingPoint:
      type: object
      properties:
        nama_efek: { type: string }
        count: { type: integer }
        kategori: { type: string }
        tingkat_keparahan:
          type: string
          enum: [ringan, sedang, serius]
    HeatmapEfek:
      type: object
      properties:
        drugs:
          type: array
          items: { type: string }
        effects:
          type: array
          items: { type: string }
        values:
          type: array
          items:
            type: array
            items: { type: integer }
    SystemStats:
      type: object
      properties:
        users_count: { type: integer }
        patients_count: { type: integer }
        drugs_count: { type: integer }
        last_scrape:
          type: object
          nullable: true
        users_by_role:
          type: object
          properties:
            tenaga_kesehatan: { type: integer }
            masyarakat: { type: integer }
            admin: { type: integer }
        process_started_at: { type: string, format: date-time }
        uptime_seconds: { type: integer }
    UserCreateRequest:
      type: object
      required: [password, role]
      properties:
        username: { type: string }
        password: { type: string, format: password }
        role:
          type: string
          enum: [tenaga_kesehatan, masyarakat, admin]
        name: { type: string }
        phone: { type: string }
paths:
  /api/health:
    get:
      summary: Liveness probe
      responses:
        "200":
          description: ok
          content:
            application/json:
              schema:
                type: object
                properties:
                  status: { type: string }
                  version: { type: string }
                  time: { type: string, format: date-time }
  /api/info:
    get:
      summary: Module loading status
      responses:
        "200":
          description: ok
  /api/auth/login:
    post:
      summary: Issue JWT
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: "#/components/schemas/LoginRequest" }
      responses:
        "200":
          description: token issued
          content:
            application/json:
              schema: { $ref: "#/components/schemas/LoginResponse" }
        "401":
          description: invalid credentials
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Error" }
  /api/auth/me:
    get:
      summary: Return current user
      security:
        - cookieAuth: []
        - bearerAuth: []
      responses:
        "200": { description: ok }
        "401":
          description: missing or invalid token
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Error" }
  /api/auth/logout:
    post:
      summary: Acknowledge logout
      responses:
        "200": { description: ok }
  /api/patients:
    get:
      summary: List patients (sorted by tanggal_kunjungan desc, id desc)
      security:
        - cookieAuth: []
        - bearerAuth: []
      responses:
        "200":
          description: list
          content:
            application/json:
              schema:
                type: array
                items: { $ref: "#/components/schemas/PatientSummary" }
        "401": { description: unauthorized }
        "403": { description: forbidden }
    post:
      summary: Create a patient (validates numeric medical fields)
      security:
        - cookieAuth: []
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: "#/components/schemas/Patient" }
      responses:
        "201":
          description: created
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Patient" }
        "400":
          description: validation failed
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Error" }
        "401": { description: unauthorized }
        "403": { description: forbidden }
  /api/patients/{pid}:
    parameters:
      - in: path
        name: pid
        required: true
        schema: { type: string, pattern: "^P[0-9]{3}$" }
    get:
      summary: Get a patient by id
      security:
        - cookieAuth: []
        - bearerAuth: []
      responses:
        "200":
          description: ok
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Patient" }
        "401": { description: unauthorized }
        "403": { description: forbidden }
        "404":
          description: not found
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Error" }
    put:
      summary: Partial update via deep merge (validates numeric fields)
      security:
        - cookieAuth: []
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: "#/components/schemas/Patient" }
      responses:
        "200":
          description: updated
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Patient" }
        "400":
          description: validation failed
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Error" }
        "404":
          description: not found
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Error" }
    delete:
      summary: Delete a patient (admin only)
      security:
        - cookieAuth: []
        - bearerAuth: []
      responses:
        "204": { description: deleted }
        "401": { description: unauthorized }
        "403": { description: forbidden }
        "404":
          description: not found
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Error" }
  /api/drugs:
    get:
      summary: List drug catalog
      parameters:
        - in: query
          name: category
          required: false
          schema: { type: string }
      responses:
        "200":
          description: ok
          content:
            application/json:
              schema:
                type: array
                items: { $ref: "#/components/schemas/DrugCatalogEntry" }
        "503":
          description: catalog unavailable
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Error" }
  /api/drugs/search:
    get:
      summary: Search drugs by name
      parameters:
        - in: query
          name: q
          required: false
          schema: { type: string }
      responses:
        "200": { description: ok }
        "503":
          description: search unavailable
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Error" }
  /api/drugs/{nama_obat}:
    parameters:
      - in: path
        name: nama_obat
        required: true
        schema: { type: string }
    get:
      summary: Get a drug safety profile
      responses:
        "200": { description: ok }
        "404":
          description: not found
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Error" }
        "503":
          description: profile unavailable
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Error" }
  /api/safety/check:
    post:
      summary: Check drug safety, optionally enriched with patient context
      security:
        - cookieAuth: []
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: "#/components/schemas/SafetyCheckRequest" }
      responses:
        "200":
          description: ok
          content:
            application/json:
              schema: { $ref: "#/components/schemas/SafetyCheckResponse" }
        "400":
          description: invalid input
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Error" }
        "401": { description: unauthorized }
        "503":
          description: safety module unavailable
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Error" }
  /api/visualizations/kunjungan-trend:
    get:
      summary: Monthly visit trend
      security:
        - cookieAuth: []
        - bearerAuth: []
      responses:
        "200":
          description: ok
          content:
            application/json:
              schema:
                type: array
                items: { $ref: "#/components/schemas/KunjunganTrendPoint" }
        "401": { description: unauthorized }
        "403": { description: forbidden }
  /api/visualizations/keluhan-distribution:
    get:
      summary: Visit category distribution
      security:
        - cookieAuth: []
        - bearerAuth: []
      responses:
        "200":
          description: ok
          content:
            application/json:
              schema:
                type: array
                items: { $ref: "#/components/schemas/KeluhanDistributionPoint" }
        "401": { description: unauthorized }
        "403": { description: forbidden }
  /api/visualizations/top-efek-samping:
    get:
      summary: Top 10 side effects from drug catalog
      security:
        - cookieAuth: []
        - bearerAuth: []
      responses:
        "200":
          description: ok
          content:
            application/json:
              schema:
                type: array
                items: { $ref: "#/components/schemas/TopEfekSampingPoint" }
        "401": { description: unauthorized }
  /api/visualizations/heatmap-efek:
    get:
      summary: Drug x effect heatmap matrix
      security:
        - cookieAuth: []
        - bearerAuth: []
      responses:
        "200":
          description: ok
          content:
            application/json:
              schema: { $ref: "#/components/schemas/HeatmapEfek" }
        "401": { description: unauthorized }
  /api/pdf/generate-rekam-medis:
    post:
      summary: Generate a single patient SOAP PDF
      security:
        - cookieAuth: []
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [pasien_id]
              properties:
                pasien_id: { type: string }
      responses:
        "200":
          description: PDF binary
          content:
            application/pdf:
              schema: { type: string, format: binary }
        "400":
          description: missing pasien_id
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Error" }
        "404":
          description: pasien not found
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Error" }
        "503":
          description: PDF module unavailable
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Error" }
  /api/pdf/generate-laporan-bulanan:
    post:
      summary: Generate aggregate monthly SOAP report (admin only)
      security:
        - cookieAuth: []
        - bearerAuth: []
      requestBody:
        required: false
        content:
          application/json:
            schema:
              type: object
              properties:
                month:
                  type: string
                  description: "YYYY-MM"
      responses:
        "200":
          description: PDF binary
          content:
            application/pdf:
              schema: { type: string, format: binary }
        "401": { description: unauthorized }
        "403": { description: forbidden }
        "503":
          description: PDF module unavailable
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Error" }
  /api/pdf/generate-efek-samping:
    post:
      summary: Generate aggregate side-effect PDF report
      security:
        - cookieAuth: []
        - bearerAuth: []
      responses:
        "200":
          description: PDF binary
          content:
            application/pdf:
              schema: { type: string, format: binary }
        "401": { description: unauthorized }
        "403": { description: forbidden }
        "503":
          description: data unavailable
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Error" }
  /api/pdf/generate-inventaris:
    post:
      summary: Generate drug inventory PDF report
      security:
        - cookieAuth: []
        - bearerAuth: []
      responses:
        "200":
          description: PDF binary
          content:
            application/pdf:
              schema: { type: string, format: binary }
        "401": { description: unauthorized }
        "403": { description: forbidden }
        "503":
          description: data unavailable
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Error" }
  /api/admin/scrape:
    post:
      summary: Trigger mocked scrape and return cached drug count
      security:
        - cookieAuth: []
        - bearerAuth: []
      responses:
        "200": { description: ok }
        "401": { description: unauthorized }
        "403": { description: forbidden }
  /api/admin/users:
    get:
      summary: List users (password fields stripped)
      security:
        - cookieAuth: []
        - bearerAuth: []
      responses:
        "200":
          description: ok
          content:
            application/json:
              schema:
                type: array
                items: { $ref: "#/components/schemas/User" }
        "401": { description: unauthorized }
        "403": { description: forbidden }
    post:
      summary: Create user account
      security:
        - cookieAuth: []
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: "#/components/schemas/UserCreateRequest" }
      responses:
        "201":
          description: created
          content:
            application/json:
              schema: { $ref: "#/components/schemas/User" }
        "400":
          description: invalid input
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Error" }
        "409":
          description: username exists
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Error" }
  /api/admin/users/{username}:
    parameters:
      - in: path
        name: username
        required: true
        schema: { type: string }
    delete:
      summary: Delete user account (refuses last admin)
      security:
        - cookieAuth: []
        - bearerAuth: []
      responses:
        "204": { description: deleted }
        "400":
          description: cannot delete last admin
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Error" }
        "401": { description: unauthorized }
        "403": { description: forbidden }
        "404":
          description: not found
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Error" }
  /api/admin/system-stats:
    get:
      summary: System counts plus process_started_at and uptime_seconds (Iterasi 1 T1-ADMIN)
      security:
        - cookieAuth: []
        - bearerAuth: []
      responses:
        "200":
          description: ok
          content:
            application/json:
              schema: { $ref: "#/components/schemas/SystemStats" }
        "401": { description: unauthorized }
        "403": { description: forbidden }
```
