# ADR-0009: Validasi field medical numerik di client dan server dengan composite parser untuk tekanan_darah

- Status: accepted
- Date: 2026-05-18
- Deciders: Ghaisan Khoirul Badruzaman (Project Leader, 251524048), Bimo Surya Anggara (QA, 251524040)

## Context and Problem Statement

Bug register entry B03 melaporkan form pasien menerima karakter huruf
ke dalam field medical numerik (BB, TB, LILA, nadi, suhu, respirasi)
serta tekanan_darah dengan format bebas. Kondisi ini menghasilkan data
non-numerik tersimpan dan menggagalkan komposisi SOAP saat ditampilkan
kembali. Field tekanan_darah memiliki format komposit `sistolik/diastolik`
(mis. `120/80`) yang tidak dapat divalidasi dengan satu angka tunggal.

## Decision Drivers

- Defense-in-depth: validasi client cepat untuk UX, validasi server
  sebagai source of truth.
- Pesan kesalahan harus Bahasa Indonesia dan menyebut label field yang
  ramah pengguna (bukan key JSON).
- Range klinis harus realistis (mis. nadi 30..220 bpm, suhu 30..44 C).
- Format tekanan_darah harus parsable sebagai dua bilangan via
  delimiter `/` dengan validasi range terpisah untuk sistolik dan
  diastolik.

## Considered Options

- Validasi hanya server-side (response 400 ke frontend).
- Validasi hanya client-side (cepat tapi rentan bypass).
- Validasi shared rule di kedua sisi dengan source code terpisah
  namun threshold yang identik.

## Decision Outcome

Chosen option: "Validasi shared rule di kedua sisi", karena memenuhi
defense-in-depth dan memberikan UX yang responsif tanpa mengorbankan
integritas data. Rentang dan regex didefinisikan di dua file
parallel sehingga drift mudah dideteksi via code review.

### Consequences

- Good: User mendapat feedback instan saat mengetik angka di luar
  range (frontend), namun submission yang lolos client tetap akan
  ditolak server jika threshold berbeda.
- Good: Tekanan darah komposit di-validasi dengan regex sederhana
  yang sama di kedua sisi, range sistolik 60..250 dan diastolik
  30..160.
- Good: Pesan kesalahan Bahasa Indonesia dengan label friendly
  (`BB (kg)`, `Suhu (C)`, `LILA (cm)`) lebih informatif daripada
  generic "invalid input".
- Bad: Threshold harus disinkronkan manual antara
  `src/lib/patient-validation.ts` dan
  `api/routes/patient_routes.py`. Tes integrasi sederhana di Iterasi 5
  dapat menjaga sinkron.
- Bad: Tidak ada single source of truth file untuk threshold; risiko
  kecil drift saat refactor.

### Confirmation

Backend rules:
- `api/routes/patient_routes.py:17-24` mendefinisikan
  `NUMERIC_RANGES` dictionary dengan tuple `(min, max, label)` untuk
  `bb_kg`, `tb_cm`, `lila_cm`, `nadi`, `suhu_c`, `respirasi`.
- `api/routes/patient_routes.py:25-27` mendefinisikan
  `SYSTOLIC_RANGE = (60.0, 250.0)`, `DIASTOLIC_RANGE = (30.0, 160.0)`,
  dan regex `TD_PATTERN`.
- `api/routes/patient_routes.py:56-99` `_validate_medical_ranges(body)`
  mengembalikan daftar string error Bahasa Indonesia.
- Dipanggil dari endpoint create:
  `api/routes/patient_routes.py:176-178` dan endpoint update:
  `api/routes/patient_routes.py:194-197`.

Frontend rules:
- `src/lib/patient-validation.ts:22-29` mendefinisikan
  `NUMERIC_RANGES` dengan `bb_kg` 1..300, `tb_cm` 30..300, `lila_cm`
  8..60, `nadi` 30..220, `suhu_c` 30..44, `respirasi` 5..80 (identik
  dengan backend).
- `src/lib/patient-validation.ts:31-32` `SYSTOLIC_RANGE = { min: 60,
  max: 250 }` dan `DIASTOLIC_RANGE = { min: 30, max: 160 }`.
- `src/lib/patient-validation.ts:34-35` regex `TD_PATTERN` dan
  `NUMERIC_ONLY`.
- `src/lib/patient-validation.ts:41-68` `validateField(key, raw)`
  menghasilkan pesan kesalahan Bahasa Indonesia per field, termasuk
  parsing tekanan_darah komposit.

## More Information

- ADR-0007 menggunakan field `tanggal_kunjungan` yang juga DD-MM-YYYY;
  pola validasi parsing mengikuti gaya yang sama (tuple parser yang
  toleran terhadap input bermasalah).
- Bug B03 didokumentasikan dalam catatan internal proyek.
