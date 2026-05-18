# ADR-0003: Skema Pasien SOAP dikanonisasi ke format anggota2 (Bimo)

- Status: accepted
- Date: 2026-05-18
- Deciders: Ghaisan Khoirul Badruzaman (Project Leader, 251524048)

## Context and Problem Statement

Tiga anggota tim menulis representasi pasien yang sedikit berbeda:
`anggota2/pasien_helper.py` (Bimo, QA) memakai ID `P001` dan struktur
SOAP bersarang; `anggota5/` (Abhidal, UI/UX) memakai draf `PSN-001`;
backend integrasi `api/` butuh memilih satu skema sebagai source of
truth agar frontend dan validasi server konsisten. Tanpa keputusan ini,
data lama anggota2/Pasien.json tidak kompatibel dengan tampilan
frontend.

## Decision Drivers

- Mandat read-only untuk file di `anggota2/`..`anggota5/` (.md
  Rule 2): perubahan skema teman tidak boleh dilakukan dari `api/`.
- Bimo sebagai pemilik domain CRUD pasien sudah melakukan validasi QA
  paling banyak terhadap skema dan ID `P001`.
- Frontend dan backend perlu skema yang sama, persis, agar
  serialization dan komposisi SOAP berfungsi tanpa adaptor per layer.

## Considered Options

- Adopsi format anggota5 (`PSN-001`) dan adaptasi anggota2 di backend.
- Adopsi format anggota2 (`P001`, struktur SOAP bersarang) dan adaptasi
  apa pun yang berbeda di backend.
- Skema baru `MWP-001` dengan migrasi dua arah.

## Decision Outcome

Chosen option: "Adopsi format anggota2 sebagai canonical", karena
sejalan dengan .md Rule 3 (table source-of-truth) yang menyatakan
`anggota2/pasien_helper.py` adalah otoritas skema Pasien, dan karena
QA artefak (test cases, test data) sudah ditulis terhadap skema ini.

### Consequences

- Good: Field key konsisten antara JSON storage (`api/data/patients.json`),
  endpoint REST, dan komponen frontend.
- Good: ID generator dapat memanggil
  `anggota2.pasien_helper.generate_id` saat tersedia, sehingga semantik
  numbering sama persis dengan modul desktop Bimo.
- Good: Tidak ada perubahan ke file anggota lain (kontrak read-only
  tetap terpenuhi).
- Bad: Draft skema `PSN-001` di anggota5 menjadi tidak dipakai untuk
  data integrasi; tim setuju karena anggota5 tidak menulis pasien di
  flow integrasi.
- Bad: Perubahan struktur SOAP di masa depan harus dimulai dari
  anggota2 atau melalui adapter wrapper, bukan diedit langsung di `api/`.

### Confirmation

- .md (root project) Rule 3 mendaftarkan
  `anggota2/pasien_helper.py` sebagai "Source of truth" untuk entitas
  Pasien dengan ID format `P001`.
- ID generator wrapper: `api/routes/patient_routes.py:102-112`
  pertama mencoba `anggota2.pasien_helper.generate_id(patients)`
  via `get_module("anggota2", "pasien_helper")`; jika tidak tersedia,
  fallback inline menghasilkan `f"P{str(next_num).zfill(3)}"` yang
  identik dengan format anggota2.
- Module header endpoint: `api/routes/patient_routes.py:1` menyatakan
  "Patient CRUD wrapping anggota2 schema. Patient IDs use Bimo's P001
  format."
- Sort tiebreak ID descending: `api/routes/patient_routes.py:48-53`
  mengekstrak tail numerik dari ID (`P001 -> 1`) sesuai format Bimo.

## More Information

- Bidan workflow reality dan mapping field optional dijelaskan dalam
  .md section "Bidan workflow reality (Pasien input/display)".
- ADR-0007 menjelaskan keputusan pengurutan terkait yang dibangun di
  atas skema kanonik ini.
- ADR-0009 menjelaskan range validation untuk field O.* numerik.
