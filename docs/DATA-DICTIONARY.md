---
title: MedWatch Data Dictionary
version: 1.0
owner: Ghaisan Khoirul Badruzaman (251524048)
date: 2026-05-18
ticket: W2-D07
scope: Backend repo (medWatch). Berlaku untuk desktop CustomTkinter (anggota1..5) dan layer web Flask (api/) yang berbagi schema yang sama.
---

# Data Dictionary MedWatch

Dokumen ini mendokumentasikan setiap entitas JSON yang dipakai oleh sistem MedWatch beserta source-of-truth file, daftar field lengkap, tipe, aturan validasi, contoh record sintetik, jalur baca/tulis, dan endpoint terkait. Setiap klaim mengutip file:line dari kode atau data nyata di repo.

Untuk konteks arsitektur penyimpanan (siapa baca-tulis di mana, kapan pakai GCS, kapan pakai file lokal), lihat bagian akhir "Storage Architecture".

Acuan kontrak schema lintas modul lihat `CLAUDE.md` Rule 3 (Schema source of truth) di `/Users/ghaisan/Documents/MedWatchIntegration/medWatch/CLAUDE.md:88`.

---

## 1. User (Akun Pengguna)

Entitas yang menyimpan kredensial dan profil pengguna yang dapat login ke layer web Flask.

- Source of truth: `api/data/users.json` (lihat `api/data/users.json:1`).
- Modul desktop lama `anggota5/data/users.json` sudah digantikan setelah migrasi Phase 1 sesuai `CLAUDE.md:73` dan `CLAUDE.md:98`.
- Loader dan persistor: `api/storage.py:101` (`load_users`) dan `api/storage.py:112` (`save_users`).
- Hashing password: bcrypt cost 12 di `api/auth.py:11` (`hash_password`).

### Field

| Field | Tipe | Wajib | Enum / Range | Deskripsi |
|---|---|---|---|---|
| `username` | string | ya | unik di seluruh file | Identitas login pengguna. Cek duplikasi di `api/routes/admin_routes.py:73`. |
| `password_hash` | string | ya | hash bcrypt dengan prefix `$2b$12$` | Disimpan setelah `hash_password` (`api/auth.py:11`). Tidak pernah dikembalikan oleh response (di-strip oleh `api/helpers.py:16`). |
| `role` | string (enum) | ya | `tenaga_kesehatan`, `masyarakat`, `admin` | Divalidasi di `api/routes/admin_routes.py:68`. Konvensi nama mengikuti `CLAUDE.md:126`. |
| `name` | string | ya (di praktik) | bebas | Nama lengkap untuk ditampilkan di UI. |
| `phone` | string | opsional | bebas, biasanya format nomor HP Indonesia 11-13 digit | Nomor kontak. Dipakai untuk generate username fallback di `api/routes/admin_routes.py:60`. |

### Contoh record (sintetik)

```json
{
  "username": "bidan_contoh",
  "role": "tenaga_kesehatan",
  "name": "Bidan Nama Contoh",
  "phone": "08xx-xxxx-xxxx",
  "password_hash": "$2b$12$XXXXXXXXXXXXXXXXXXXXXX"
}
```

### Read / write

- Dibaca oleh: `api/routes/auth_routes.py:22` (login), `api/routes/admin_routes.py:44` (list users), `api/routes/admin_routes.py:109` (system stats), `api/middleware.py:17` (decoder JWT, indirect via `g.user`).
- Ditulis oleh: `api/routes/admin_routes.py:83` (create), `api/routes/admin_routes.py:101` (delete). Penulisan disalurkan ke `save_users` di `api/storage.py:112`.

### Endpoint terkait

- `POST /api/auth/login` -> `api/routes/auth_routes.py:13`
- `GET /api/admin/users` -> `api/routes/admin_routes.py:42`
- `POST /api/admin/users` -> `api/routes/admin_routes.py:49`
- `DELETE /api/admin/users/<username>` -> `api/routes/admin_routes.py:89`

---

## 2. Patient (Pasien) - Skema SOAP

Entitas catatan pasien dengan struktur SOAP (Subjective, Objective, Assessment, Plan). Skema kanonik mengikuti format Bimo (anggota2).

- Source of truth: `api/data/patients.json` (lihat `api/data/patients.json:1`).
- Skema referensi historis di `anggota2/Pasien.json` (file desktop) bersifat read-only sesuai `CLAUDE.md:73`.
- Loader/persistor: `api/storage.py:116` (`load_patients`), `api/storage.py:121` (`save_patients`).
- Generator ID: `api/routes/patient_routes.py:102` dengan fallback ke `anggota2/pasien_helper.py:27` (`generate_id`).
- Validator numerik server-side: `api/routes/patient_routes.py:56` (`_validate_medical_ranges`).
- Validator numerik client-side (mirror): `src/lib/patient-validation.ts:22` di repo frontend.

### Field

| Field | Tipe | Wajib | Enum / Range | Deskripsi |
|---|---|---|---|---|
| `id` | string | otomatis | format `P###` (P + 3 digit) | Dibuat oleh `_generate_id` (`api/routes/patient_routes.py:102`). |
| `nama` | string | ya | bebas | Wajib. Lihat penegakan di `api/routes/patient_routes.py:166`. |
| `umur` | string | opsional | biasanya angka tahun | Disimpan sebagai string sesuai data eksisting (`api/data/patients.json:5`). |
| `alamat` | string | opsional | bebas | Alamat singkat. |
| `kategori` | string | opsional | contoh isian di data: `Ibu Hamil`, `Lansia`, `Anak`, `Umum` | Bebas-text yang dipakai untuk filter. |
| `tanggal_kunjungan` | string | opsional (disarankan) | format `DD-MM-YYYY` | Parser di `api/routes/patient_routes.py:30`. |
| `created_by` | string | otomatis | sama dengan `users.username` | Diisi otomatis dari `g.user["username"]` di `api/routes/patient_routes.py:183`. |
| `S` | object | ya | nested | Subjective. |
| `S.keluhan` | string | ya | bebas | Wajib (`api/routes/patient_routes.py:168`). |
| `S.riwayat` | string | opsional | bebas | Riwayat penyakit / alergi / kehamilan. |
| `O` | object | opsional | nested | Objective. Diisi sebagian sesuai realitas pemeriksaan bidan (`CLAUDE.md:118`). |
| `O.tekanan_darah` | string | opsional | format `<sistolik>/<diastolik>`. Sistolik 60-250, diastolik 30-160 | Pola regex di `api/routes/patient_routes.py:27`; range di `api/routes/patient_routes.py:25` dan `26`. |
| `O.nadi` | string (numerik) | opsional | 30-220 | `NUMERIC_RANGES["nadi"]` di `api/routes/patient_routes.py:21`. |
| `O.suhu_c` | string (numerik) | opsional | 30-44 (Celsius) | `NUMERIC_RANGES["suhu_c"]` di `api/routes/patient_routes.py:22`. |
| `O.respirasi` | string (numerik) | opsional | 5-80 | `NUMERIC_RANGES["respirasi"]` di `api/routes/patient_routes.py:23`. |
| `O.bb_kg` | string (numerik) | opsional | 1-300 | `NUMERIC_RANGES["bb_kg"]` di `api/routes/patient_routes.py:18`. |
| `O.tb_cm` | string (numerik) | opsional | 30-300 | `NUMERIC_RANGES["tb_cm"]` di `api/routes/patient_routes.py:19`. |
| `O.lila_cm` | string (numerik) | opsional | 8-60 | `NUMERIC_RANGES["lila_cm"]` di `api/routes/patient_routes.py:20`. |
| `O.catatan` | string | opsional | bebas (multi-line OK) | Catch-all untuk observasi non-struktur. |
| `A` | object | ya | nested | Assessment. |
| `A.diagnosa` | string | ya | bebas | Wajib (`api/routes/patient_routes.py:170`). |
| `P` | object | ya | nested | Plan. |
| `P.tindakan` | string | ya | bebas, multi-line (`\n`) | Wajib (`api/routes/patient_routes.py:172`). |
| `P.resep` | string | opsional | bebas, multi-line atau dipisah `,`/`;` | Diparsing oleh `parse_resep_to_meds` di `api/helpers.py:47`. |
| `P.jadwal_kontrol` | string | opsional | format `DD-MM-YYYY` atau bebas | Tanggal kontrol berikutnya. |

Catatan: nilai numerik kosong (`""`) dianggap "tidak diisi" dan tidak gagal validasi (`api/routes/patient_routes.py:87`).

### Contoh record (sintetik)

```json
{
  "id": "P001",
  "tanggal_kunjungan": "18-05-2026",
  "nama": "Nama Contoh",
  "umur": "25",
  "alamat": "Kp. Contoh",
  "kategori": "Ibu Hamil",
  "S": {
    "keluhan": "mual dan pusing",
    "riwayat": ""
  },
  "O": {
    "tekanan_darah": "110/70",
    "nadi": "",
    "suhu_c": "",
    "respirasi": "",
    "bb_kg": "50",
    "tb_cm": "150",
    "lila_cm": "23",
    "catatan": "tespek positif"
  },
  "A": { "diagnosa": "G1P0A0 hamil 5 mg" },
  "P": {
    "tindakan": "Istirahat cukup\nMakan sedikit tapi sering",
    "resep": "Asam folat 1x1 sehari",
    "jadwal_kontrol": ""
  },
  "created_by": "bidan_contoh"
}
```

### Read / write

- Dibaca oleh: `api/routes/patient_routes.py:138` (list), `:152` (get-by-id), `api/routes/safety_routes.py:47` (untuk pasien_context), `api/routes/admin_routes.py:110` (system stats).
- Ditulis oleh: `api/routes/patient_routes.py:184` (create), `:201` (update), `:213` (delete).

### Endpoint terkait

- `GET /api/patients` -> `api/routes/patient_routes.py:135`
- `GET /api/patients/<pid>` -> `api/routes/patient_routes.py:149`
- `POST /api/patients` -> `api/routes/patient_routes.py:162`
- `PUT /api/patients/<pid>` -> `api/routes/patient_routes.py:190`
- `DELETE /api/patients/<pid>` -> `api/routes/patient_routes.py:208`

---

## 3. Drug (Database Obat)

Entitas obat kanonik dengan informasi farmakologi. Format Iqbal (anggota4) sesuai `CLAUDE.md:95`.

- Source of truth: `anggota4/data/drug_database.json` (lihat `anggota4/data/drug_database.json:1`).
- Loader: `anggota4/data_loader.py` (dipanggil via `bootstrap.get_module("anggota4", "data_loader")` di `api/routes/admin_routes.py:28`).
- File ini bersifat read-only bagi layer web (`CLAUDE.md:73`).

### Field

| Field | Tipe | Wajib | Enum / Range | Deskripsi |
|---|---|---|---|---|
| `nama_obat` | string | ya | bebas | Nama generik / INN obat. |
| `alias` | array string | opsional | bebas | Daftar nama dagang / sinonim. Contoh: `["Acetaminophen"]` (`anggota4/data/drug_database.json:5`). |
| `kategori` | string | ya | contoh: `Analgesik dan antipiretik`, `Antibiotik penisilin`, `ACE inhibitor`, `Antihistamin`, `Antidiabetik oral biguanid`, `OAINS / antiinflamasi nonsteroid` | Kategori terapeutik bebas-text. |
| `bahan_aktif` | array string | ya | bebas | Daftar zat aktif. |
| `indikasi` | array string | ya | bebas | Daftar indikasi klinis. |
| `dosis_umum` | string | ya | bebas | Pedoman dosis umum dewasa. |
| `kehamilan` | string | ya | bebas (contoh: `Kategori B, umumnya aman bila sesuai dosis.`) | Catatan keamanan kehamilan. |
| `peringatan` | array string | opsional | bebas | Daftar peringatan klinis. |
| `kontraindikasi` | array string | opsional | bebas | Daftar kontraindikasi. |
| `interaksi` | array string | opsional | bebas | Daftar interaksi dengan obat / makanan lain. |
| `efek_samping` | array string | opsional | nama efek samping yang harus cocok dengan `effect_database.json.nama_efek` agar bisa di-cross-reference oleh `cross_reference_efek_obat` (`anggota4/safety_checker.py:43`) | Daftar efek samping. |

### Contoh record (sintetik)

```json
{
  "nama_obat": "Paracetamol",
  "alias": ["Acetaminophen"],
  "kategori": "Analgesik dan antipiretik",
  "bahan_aktif": ["Paracetamol"],
  "indikasi": ["Demam", "Nyeri ringan sampai sedang"],
  "dosis_umum": "500 mg setiap 4-6 jam bila perlu, maksimal 4 gram per hari.",
  "kehamilan": "Kategori B, umumnya aman bila sesuai dosis.",
  "peringatan": [
    "Gunakan hati-hati pada pasien dengan gangguan fungsi hati."
  ],
  "kontraindikasi": [
    "Hipersensitivitas terhadap paracetamol."
  ],
  "interaksi": [
    "Warfarin dapat meningkatkan risiko perdarahan bila dipakai jangka panjang."
  ],
  "efek_samping": [
    "Mual",
    "Ruam kulit",
    "Peningkatan enzim hati",
    "Reaksi alergi berat"
  ]
}
```

### Read / write

- Dibaca oleh: `anggota4/safety_checker.py:48` via `buat_index_efek_samping`, `anggota4/safety_checker.py:180` via `ambil_obat_terbaik`, dan jalur web `api/routes/safety_routes.py:26`.
- Ditulis: read-only di alur normal. Refresh massal melalui `anggota1/openfda/fetch.py` (target file beda, lihat entitas 5).

### Endpoint terkait

- `POST /api/safety/check` -> `api/routes/safety_routes.py:16`
- Endpoint list/detail obat di blueprint `api/routes/drug_routes.py` (di-mount di `api/app.py`).

---

## 4. SideEffect (Efek Samping)

Master database efek samping dengan tingkat keparahan dan rekomendasi penanganan.

- Source of truth: `anggota4/data/effect_database.json` (lihat `anggota4/data/effect_database.json:1`).
- Bobot keparahan: `ringan = 1`, `sedang = 2`, `serius = 4` di `anggota4/safety_checker.py:14` (`BOBOT_KEPARAHAN`).
- Urutan untuk sortir: `serius = 0`, `sedang = 1`, `ringan = 2` di `anggota4/safety_checker.py:15` (`URUTAN_KEPARAHAN`).
- Skor risiko 0-100 dihitung di `anggota4/safety_checker.py:18` (`_hitung_skor_risiko`); label `tinggi >= 70`, `sedang >= 40`, sisanya `rendah` di `anggota4/safety_checker.py:34` (`_label_risiko`).

### Field

| Field | Tipe | Wajib | Enum / Range | Deskripsi |
|---|---|---|---|---|
| `nama_efek` | string | ya | unik di file | Nama efek samping kanonik. Dipakai sebagai key cross-reference dengan `drug_database.json.efek_samping`. |
| `kategori` | string | ya | contoh: `Gastrointestinal`, `Dermatologis`, `Hepatik`, `Imunologis`, `Neurologis`, `Renal`, `Kardiovaskular`, `Respirasi`, `Metabolik` | Kategori klinis efek. |
| `tingkat_keparahan` | string (enum) | ya | `ringan`, `sedang`, `serius` | Skala internal Iqbal. Dipakai untuk skoring risiko di `anggota4/safety_checker.py:26`. |
| `rekomendasi` | string | ya | bebas | Rekomendasi penanganan / tindak lanjut. |

### Contoh record (sintetik)

```json
{
  "nama_efek": "Mual",
  "kategori": "Gastrointestinal",
  "tingkat_keparahan": "ringan",
  "rekomendasi": "Pantau keluhan dan anjurkan konsumsi obat setelah makan bila memungkinkan."
}
```

### Read / write

- Dibaca oleh: `anggota4/safety_checker.py:48` (`buat_index_efek_samping`) dan implisit oleh API `POST /api/safety/check`.
- Ditulis: read-only di alur web (`CLAUDE.md:73`).

### Endpoint terkait

- `POST /api/safety/check` -> `api/routes/safety_routes.py:16`.

---

## 5. AdverseEvent (openFDA Reaction)

Hasil agregasi adverse event per obat dari sumber FAERS / openFDA. Baru ditambahkan di Wave 1 tiket T1-DATA.

- Source of truth: `anggota1/data/drug_safety_data.json` (lihat `anggota1/data/drug_safety_data.json:1`).
- Producer: `anggota1/openfda/fetch.py:257` (`fetch_adverse_events_for_drug`) dan loop utama `anggota1/openfda/fetch.py:494`.
- Total record yang sudah benar-benar diunduh: 74 obat, 1850 total reaction terms (terverifikasi via `python3 -c` count, sumber file lokal real).
- API key tidak pernah ditulis ke file: lihat redaksi di `anggota1/openfda/fetch.py:156` (`_redact_params`).

### Field

| Field | Tipe | Wajib | Enum / Range | Deskripsi |
|---|---|---|---|---|
| `drug_name` | string | ya | bebas, biasanya Title Case INN | Nama obat. Sesuai `anggota1/openfda/fetch.py:343`. |
| `category` | string | ya | hasil `tebak_kategori` (`anggota1/openfda/fetch.py:136`) | Kategori coarse: `Analgesik`, `Antibiotik`, `Antihistamin`, `Antidepresan`, `Antihipertensi`, `Statin`, `Antitrombotik`, `Antidiabetik`, `Saluran Cerna`, `Kortikosteroid`, `Saluran Napas`, `Hormon Tiroid`, `Anti-gout`, `Umum`. |
| `side_effects` | array string | ya | top-N reaksi MedDRA Title Case (N <= 25 per `anggota1/openfda/fetch.py:61` `EVENT_COUNT_LIMIT`) | Daftar nama reaksi adverse event paling sering dilaporkan. |
| `severity_level` | string (enum) | ya | `ringan`, `sedang`, `serius` | Diturunkan dari fraksi `serious` dan `death` di `anggota1/openfda/fetch.py:236` (`_severity_from_event_aggregate`). |
| `warnings` | string | ya | kalimat Bahasa Indonesia | Ringkasan dalam Bahasa Indonesia. Pattern di `anggota1/openfda/fetch.py:334`. |
| `source_url` | string | ya | URL openFDA dengan `api_key=<redacted>` | URL traceability dengan API key sudah diredaksi (`anggota1/openfda/fetch.py:442`). |

### Contoh record (sintetik, terinspirasi dari record real Paracetamol)

```json
{
  "drug_name": "Paracetamol",
  "category": "Analgesik",
  "side_effects": [
    "Vomiting",
    "Nausea",
    "Pyrexia",
    "Dyspnoea",
    "Fatigue",
    "Headache"
  ],
  "severity_level": "serius",
  "warnings": "Berdasarkan 111361 laporan FAERS untuk paracetamol, fraksi laporan serius 96%, fraksi laporan kematian 14.1%. Konsultasikan dengan tenaga kesehatan dan rujuk monograph BPOM atau FDA Drugs sebelum digunakan.",
  "source_url": "https://api.fda.gov/drug/event.json?search=patient.drug.medicinalproduct:\"paracetamol\"&api_key=<redacted>&count=patient.reaction.reactionmeddrapt.exact&limit=25"
}
```

### Read / write

- Dibaca oleh: visualisasi `anggota3/NewestVisualization/` (read-only) dan endpoint yang menampilkan ringkasan FAERS.
- Ditulis hanya oleh `anggota1/openfda/fetch.py:521` saat orchestrator `main()` dijalankan dengan env `OPENFDA_API_KEY` di-set (`anggota1/openfda/fetch.py:501`).

### Endpoint terkait

- Tidak ada endpoint REST yang khusus mengembalikan adverse_events; data ini dikonsumsi oleh modul visualisasi (Alia) dan dapat ditampilkan via halaman scraping.

---

## 6. Recall (Drug Recall Enforcement)

Catatan penarikan obat dari FDA Drug Enforcement Reports.

- Source of truth: `anggota1/data/drug_recalls.json` (lihat `anggota1/data/drug_recalls.json:1`).
- Producer: `anggota1/openfda/fetch.py:389` (`fetch_drug_recalls`).
- Total record yang sudah benar-benar diunduh: 6000 recall (terverifikasi via `python3 -c` count pada file lokal).
- Severity class set (real): `Class I`, `Class II`, `Class III`, dan `Not Yet Classified` (terverifikasi via inspeksi file).

### Field

| Field | Tipe | Wajib | Enum / Range | Deskripsi |
|---|---|---|---|---|
| `product_name` | string | ya | maksimal 240 karakter | Deskripsi produk (dipotong di `anggota1/openfda/fetch.py:423`). |
| `reason` | string | ya | maksimal 500 karakter | Alasan recall (dipotong di `anggota1/openfda/fetch.py:424`). |
| `recall_date` | string | ya | format `YYYY-MM-DD` (atau `""` bila tidak dapat diparsing) | Hasil parsing `recall_initiation_date` di `anggota1/openfda/fetch.py:359` (`_parse_recall_date`). |
| `severity_class` | string (enum) | ya | `Class I`, `Class II`, `Class III`, `Not Yet Classified`, atau nilai literal lain bila tidak cocok | Hasil normalisasi di `anggota1/openfda/fetch.py:373` (`_coerce_classification`). |
| `company` | string | ya | maksimal 200 karakter; default `"Tidak diketahui"` bila kosong | Nama firma yang menarik produk (`anggota1/openfda/fetch.py:427`). |

### Contoh record (sintetik)

```json
{
  "product_name": "Contoh Eye Drops 10 mL, Sterile, Distributed by Contoh Pharma Inc., NDC 00000-000-00",
  "reason": "Lack of Assurance of Sterility: CGMP deviations during FDA inspection.",
  "recall_date": "2026-04-23",
  "severity_class": "Class II",
  "company": "Contoh Pharma, Inc."
}
```

### Read / write

- Dibaca oleh: visualisasi `anggota3/NewestVisualization/` (heatmap, statistik recall) dan halaman scraping di frontend.
- Ditulis hanya oleh `anggota1/openfda/fetch.py:542` saat orchestrator `main()` dijalankan.

### Endpoint terkait

- Tidak ada endpoint REST khusus; konsumsi melalui modul desktop dan visualisasi.

---

## 7. AdminStats (Response GET /api/admin/system-stats)

Bentuk respons endpoint dashboard admin. Diperbarui di tiket Wave 1 T1-ADMIN untuk mengganti nilai hardcoded.

- Source of truth: handler `api/routes/admin_routes.py:106` (`system_stats`).
- Bukan file persistent; nilai dihitung saat request.

### Field

| Field | Tipe | Wajib | Range / Catatan | Deskripsi |
|---|---|---|---|---|
| `users_count` | integer >= 0 | ya | - | Jumlah user dari `load_users()` (`api/routes/admin_routes.py:109`). |
| `patients_count` | integer >= 0 | ya | - | Jumlah pasien dari `load_patients()` (`api/routes/admin_routes.py:110`). |
| `drugs_count` | integer >= 0 | ya | - | Jumlah obat dari modul `anggota4.data_loader.muat_database_obat()` (`api/routes/admin_routes.py:112`). |
| `last_scrape` | object \| null | ya | berisi `status`, `drugs_updated`, `recalls_added`, `source`, `timestamp` ISO 8601 UTC | Hasil scraper terakhir, atau `null` jika belum pernah dijalankan sesi ini (`api/routes/admin_routes.py:119`). |
| `users_by_role` | object | ya | keys: `tenaga_kesehatan`, `masyarakat`, `admin` (integer >= 0) | Breakdown peran pengguna (`api/routes/admin_routes.py:120`). |
| `process_started_at` | string ISO 8601 UTC | ya | timestamp UTC | Waktu startup proses backend, dicatat di module-import (`api/routes/admin_routes.py:18`). |
| `uptime_seconds` | integer >= 0 | ya | dalam detik | `(now - process_started_at).total_seconds()` (`api/routes/admin_routes.py:114`). |

### Contoh respons (sintetik)

```json
{
  "users_count": 6,
  "patients_count": 14,
  "drugs_count": 6,
  "last_scrape": {
    "status": "completed",
    "drugs_updated": 6,
    "recalls_added": 0,
    "source": "cached",
    "timestamp": "2026-05-18T07:00:00+00:00"
  },
  "users_by_role": {
    "tenaga_kesehatan": 2,
    "masyarakat": 2,
    "admin": 2
  },
  "process_started_at": "2026-05-18T06:55:00+00:00",
  "uptime_seconds": 300
}
```

### Read / write

- Dihasilkan secara langsung saat dipanggil; tidak ditulis ke file.

### Endpoint terkait

- `GET /api/admin/system-stats` -> `api/routes/admin_routes.py:106`.

---

## 8. AuthToken (JWT Payload)

Token autentikasi yang diterbitkan saat login berhasil. Algoritma HS256.

- Penerbit: `api/auth.py:22` (`issue_token`).
- Verifier: `api/auth.py:35` (`verify_token`).
- Algoritma dan masa berlaku: HS256 dengan kedaluwarsa 12 jam, dari `api/config.py:18` (`JWT_ALGORITHM`) dan `api/config.py:19` (`JWT_EXPIRY_HOURS`).
- Kunci tanda tangan: env `JWT_SECRET` (`api/config.py:17`). Nilai tidak pernah ditulis ke kode, log, atau dokumen.

### Field (claims JWT)

| Field | Tipe | Wajib | Range / Catatan | Deskripsi |
|---|---|---|---|---|
| `sub` | string | ya | sama dengan `users.username` | Subject (username login). Lihat `api/auth.py:25`. |
| `role` | string (enum) | ya | `tenaga_kesehatan`, `masyarakat`, `admin` | Peran yang dipakai oleh middleware `require_role` (`api/middleware.py:37`). |
| `name` | string | ya | sesuai `users.name` | Nama tampilan. |
| `iat` | integer (UNIX seconds) | ya | UTC | Issued-at, set ke timestamp UTC sekarang (`api/auth.py:28`). |
| `exp` | integer (UNIX seconds) | ya | `iat + 12 jam` | Kedaluwarsa (`api/auth.py:29`). |
| `iss` | string | ya | nilai konstan `medwatch-api` | Issuer claim. Diverifikasi oleh `jwt.decode(... issuer="medwatch-api")` (`api/auth.py:37`). |

### Contoh payload (sintetik, untuk ilustrasi)

```json
{
  "sub": "bidan_contoh",
  "role": "tenaga_kesehatan",
  "name": "Bidan Nama Contoh",
  "iat": 1747560000,
  "exp": 1747603200,
  "iss": "medwatch-api"
}
```

### Read / write

- Diterbitkan oleh `POST /api/auth/login` (`api/routes/auth_routes.py:26`).
- Diverifikasi oleh `require_auth` (`api/middleware.py:17`) yang dipanggil oleh semua endpoint terproteksi.
- Setelah diverifikasi, payload mengisi `g.user` (`api/middleware.py:28`) yang dibaca oleh route handler.

### Endpoint terkait

- `POST /api/auth/login` -> `api/routes/auth_routes.py:13`
- `GET /api/auth/me` -> `api/routes/auth_routes.py:43`
- Seluruh endpoint dengan dekorator `require_auth` atau `require_role`.

---

## Storage Architecture

Bagian ini menjelaskan kontrak penyimpanan: siapa baca, siapa tulis, di mana datanya, dan bagaimana skema desktop versus web tetap konsisten.

### 1. Dua jalur penyimpanan, satu schema

Setiap entitas di atas dipakai oleh dua jalur klien:

- **Jalur desktop CustomTkinter (anggota1..5)**. Setiap anggota memiliki direktori `anggota{N}/data/` sendiri. File JSON dibaca-tulis langsung dengan `json.load`/`json.dump` (contoh: `anggota2/pasien_helper.py:13` dan `:21`).
- **Jalur web Flask (`api/`)**. Layer web menyimpan salinan terpisah di `api/data/` (`api/config.py:7`). Loader/persistor terpusat di `api/storage.py`. Skema field identik dengan jalur desktop.

Pemisahan ini mengikuti `CLAUDE.md:73`: file JSON eksisting di `anggota{N}/data/` adalah read-only bagi layer web; layer web memelihara salinannya sendiri di `api/data/`.

### 2. Read-only versus read-write per file

| File | Owner | Akses dari layer web |
|---|---|---|
| `api/data/users.json` | Layer web (Ghaisan, integrasi) | Baca dan tulis |
| `api/data/patients.json` | Layer web (Ghaisan, integrasi) | Baca dan tulis |
| `anggota2/Pasien.json` | Bimo (desktop) | Tidak diakses oleh layer web (jalur web pakai `api/data/patients.json` saja) |
| `anggota4/data/drug_database.json` | Iqbal (desktop) | Baca (read-only) via `bootstrap.get_module("anggota4", "data_loader")` di `api/routes/admin_routes.py:28` dan `:111` |
| `anggota4/data/effect_database.json` | Iqbal (desktop) | Baca (read-only) via `anggota4/safety_checker.py:48` saat `POST /api/safety/check` (`api/routes/safety_routes.py:30`) |
| `anggota1/data/drug_safety_data.json` | Ghaisan (scraping) | Baca (read-only) |
| `anggota1/data/drug_recalls.json` | Ghaisan (scraping) | Baca (read-only) |
| `anggota5/data/users.json` | Sudah digantikan oleh `api/data/users.json` setelah Phase 1 (`CLAUDE.md:73`, `CLAUDE.md:98`) | Tidak dipakai layer web |

### 3. Local file vs Google Cloud Storage

Layer web mendukung dua backend penyimpanan, dipilih dengan env `USE_CLOUD_STORAGE` (`api/config.py:29`).

| Mode | Pemicu | Lokasi data |
|---|---|---|
| Local | `USE_CLOUD_STORAGE != "true"` (default, dev lokal) | `api/data/<file>.json` di filesystem lokal. Lihat `_load_local` (`api/storage.py:30`) dan `_save_local` (`api/storage.py:38`). |
| Cloud Storage | `USE_CLOUD_STORAGE == "true"` (Cloud Run) | Bucket GCS `medwatch-polban-2026-state` di proyek `medwatch-polban-2026`. Nama bucket dan project dari `api/config.py:27` dan `:28`. Lihat `_load_gcs` (`api/storage.py:45`) dan `_save_gcs` (`api/storage.py:55`). |

Saat Cloud Storage aktif dan blob tidak ditemukan, loader otomatis seed dari file lokal sebagai bootstrap satu kali (`api/storage.py:67-71`). Mekanisme ini menjamin penampakan data awal saat container Cloud Run pertama kali dideploy.

### 4. Hashing password "lazy upgrade"

Jika seed `users.json` mengandung field `password_plain` (bukan `password_hash`), loader `load_users` akan otomatis mem-bcrypt-kan password tersebut dan menyimpan kembali file dengan `password_hash` (`api/storage.py:90` `_ensure_users_hashed`, dipanggil di `api/storage.py:105`). Setelah commit pertama backend, `password_plain` tidak pernah lagi muncul di disk. Mekanisme ini sengaja: developer convenience saat seeding, tetapi nilai plaintext tidak persist (`api/storage.py:1-7`).

### 5. Adapter desktop -> integrasi (opsional)

`integrasi/adapter.py:19` (`jalankan_scraper`), `:35` (`jalankan_pasien_crud`), `:46` (`jalankan_visualisasi`), `:51` (`jalankan_tkesehatan_crud`), dan `:67` (`jalankan_export_pdf`) menyediakan jembatan jika menu terpadu desktop (`integrasi/app_terpadu.py`) ingin memanggil flow desktop di anggota1..5. Adapter ini tidak mengganggu skema data: tetap menulis ke file `anggota{N}/data/...` yang sama, dengan skema yang sama dengan jalur web. Kerangka kontrak schema diatur oleh `CLAUDE.md:88-98` (Schema source of truth).

### 6. Aturan kerahasiaan kredensial di storage

- `password_hash` tidak pernah dikembalikan ke klien: di-strip oleh `strip_password_fields` (`api/helpers.py:16`) di setiap response yang menyentuh user.
- `JWT_SECRET` hanya dibaca dari env (`api/config.py:17`) dan tidak pernah ditulis ke file.
- `OPENFDA_API_KEY` dibaca dari env (`api/config.py:34`) dan diredaksi sebelum di-log atau ditulis ke `source_url` (`anggota1/openfda/fetch.py:156` `_redact_params`, `:442` `_build_source_url`).
- Aturan ini selaras dengan `.mission/plan.md` constraint 12 dan `CLAUDE.md` Mission Protocol.

### 7. Konsistensi skema desktop vs web

Konsep: skema field di JSON desktop dan JSON web identik. Yang berbeda hanya jalur baca-tulis. Contoh: `Patient (Pasien)` baik di `api/data/patients.json` maupun di `anggota2/Pasien.json` memakai field `S`/`O`/`A`/`P` yang sama. Bila terjadi konflik formal (mis. ID `PSN-001` lama dari anggota5 vs `P001` Bimo), kanonikal mengacu ke Bimo's `P###` sesuai `CLAUDE.md:94`. Validasi numerik server-side (`api/routes/patient_routes.py:17-99`) menjadi guard untuk menjaga data web tetap pada ranges yang sama dengan validator client-side (`src/lib/patient-validation.ts:22-32`).

---

## Referensi silang

- Skema kanonik per entitas: `CLAUDE.md:88-98` (Schema source of truth).
- Workflow bidan dan field opsional di Pasien: `CLAUDE.md:100-122`.
- Konstanta validasi numerik server: `api/routes/patient_routes.py:17-99`.
- Konstanta validasi numerik client: `src/lib/patient-validation.ts:22-32` (repo frontend).
- Auth + JWT: `api/auth.py`, `api/middleware.py`, `api/config.py:17-19`.
- Storage backend: `api/storage.py`, `api/config.py:27-29`.
- Producer adverse event + recall: `anggota1/openfda/fetch.py`.
- Producer drug + side_effect (statis, read-only bagi web): `anggota4/data/drug_database.json`, `anggota4/data/effect_database.json`.
