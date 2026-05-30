# ADR-0008: Endpoint PDF efek-samping dan inventaris di-implementasi in-process dengan fpdf2 di api/

- Status: accepted
- Date: 2026-05-18
- Deciders: Ghaisan Khoirul Badruzaman (Project Leader, 251524048), Abhidal Muhammad Gazza (UI/UX, 251524032)

## Context and Problem Statement

Frontend menampilkan tombol export PDF untuk beberapa konteks
(rekam medis SOAP per pasien, laporan bulanan, laporan efek samping,
dan laporan inventaris obat). Modul `anggota5/export_pdf.py` milik
Abhidal sudah menutup kasus SOAP dan laporan bulanan dengan baik.
Untuk laporan efek samping dan inventaris, opsi yang tersedia adalah
mengedit `anggota5/export_pdf.py` (membuat fungsi baru di sana) atau
membangun generator baru langsung di layer integrasi `api/`.

## Decision Drivers

- Mandat read-only untuk file anggota selain pengecualian Iterasi 1
  anggota5 yang sudah ditutup (konvensi proyek).
- Scope discipline: hanya tambah file di layer integrasi `api/`,
  jangan menyentuh file teman.
- Library yang sama (`fpdf2`) sudah dipakai modul anggota5 sehingga
  output PDF (font, margin, encoding) tetap konsisten.

## Considered Options

- Tambahkan fungsi `export_efek_samping_pdf` dan `export_inventaris_pdf`
  ke `anggota5/export_pdf.py`.
- Buat generator baru di `api/routes/pdf_routes.py` dengan kelas
  helper sendiri menggunakan `fpdf2`.
- Render PDF di frontend (browser print-to-PDF atau jspdf) tanpa
  endpoint backend.

## Decision Outcome

Chosen option: "Generator baru in-process di `api/routes/pdf_routes.py`
dengan `fpdf2`", karena memenuhi kontrak read-only, menjaga binari
output identik dengan generator Abhidal (font helvetica Latin-1),
dan tidak menambah dependency baru.

### Consequences

- Good: Tidak ada file anggota5 yang berubah; QA Abhidal terhadap
  generator SOAP tetap valid.
- Good: Endpoint baru `/api/pdf/generate-efek-samping` dan
  `/api/pdf/generate-inventaris` dapat dipanggil dengan auth yang sama
  (decorator role) sebagai endpoint PDF lainnya.
- Good: Helper umum `MedWatchReportPDF` (header + footer) didefinisikan
  satu kali dan dipakai oleh kedua report; layout konsisten.
- Bad: Ada dua tempat yang memakai `fpdf2` di repo (anggota5 dan
  api/), keduanya harus diawasi saat upgrade library di masa depan.
- Bad: Logic encoding latin-1 (`_safe()`) di-duplicate dengan logika
  serupa di anggota5; risiko kecil drift.

### Confirmation

- Module docstring memetakan keputusan ini secara eksplisit:
  `api/routes/pdf_routes.py:1-13` menyatakan "Two categories of
  generator live here: 1. Per-patient and aggregate SOAP reports
  delegated to anggota5/export_pdf ... 2. Drug safety and inventory
  reports built directly with fpdf2 here (efek-samping, inventaris).
  These read anggota1/drug_safety_data.json and
  anggota4/drug_database.json read-only and never modify anggota source
  files."
- Endpoint efek-samping: `api/routes/pdf_routes.py:241` (route
  `/api/pdf/generate-efek-samping`).
- Endpoint inventaris: `api/routes/pdf_routes.py:388-390` (route
  `/api/pdf/generate-inventaris`, function `generate_inventaris`).
- Helper umum: `api/routes/pdf_routes.py:48-51` `MedWatchReportPDF
  (FPDF)` mendefinisikan header dan footer reusable.
- Encoding safe: `api/routes/pdf_routes.py:42-45` `_safe()` melakukan
  encoding latin-1 untuk font helvetica.

## More Information

- ADR-0003 (skema canonical anggota2) menjelaskan kenapa SOAP-related
  PDF tetap delegasi ke anggota5 (skema sudah ditulis di sana).
- Endpoint SOAP rekam-medis dan laporan-bulanan di file yang sama
  memang delegasi via `bootstrap.get_module("anggota5",
  "export_pdf")`, tidak duplikasi.
