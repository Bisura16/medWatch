# ADR-0007: Daftar pasien diurutkan newest-first dengan parser DD-MM-YYYY dan tiebreak id descending

- Status: accepted
- Date: 2026-05-18
- Deciders: Ghaisan Khoirul Badruzaman (Project Leader, 251524048), Bimo Surya Anggara (QA, 251524040)

## Context and Problem Statement

Bug register entry B07 melaporkan bahwa daftar pasien menampilkan
kunjungan terbaru di bawah, sehingga bidan harus scroll untuk
menemukan pasien yang baru saja masuk. Locale yang dipakai untuk
`tanggal_kunjungan` adalah format Indonesia DD-MM-YYYY (lihat .md
Rule 3 skema Visit/SOAP). Sorting alfabetis terhadap string DD-MM-YYYY
tidak menghasilkan urutan kronologis yang benar, dan sorting di
frontend tidak dapat mengandalkan parser bawaan `Date(...)` karena
ambiguitas dengan format Amerika MM-DD-YYYY.

## Decision Drivers

- Bidan mengharapkan pasien terbaru di atas tanpa perlu interaksi.
- Skema `tanggal_kunjungan` adalah string DD-MM-YYYY (Indonesia).
- ID pasien `P001` monotonic; tiebreak harus deterministik.
- Sorting harus terjadi di server agar response API konsisten antar
  klien (mobile, desktop) dan tidak bergantung pada locale Date parser
  browser.

## Considered Options

- Sort client-side menggunakan `Date.parse` (rentan ambiguitas locale).
- Sort server-side dengan `datetime.strptime(s, "%d-%m-%Y")` (memerlukan
  semua tanggal valid).
- Sort server-side dengan parser tuple `(y, m, d)` manual yang
  toleran terhadap data corrupt.

## Decision Outcome

Chosen option: "Sort server-side dengan parser tuple toleran +
tiebreak id descending", karena memberikan urutan yang konsisten
secara API, tidak crash pada data corrupt (tanggal kosong atau
malformed), dan menjadikan baris terbaru selalu di atas dengan tiebreak
yang dapat diprediksi.

### Consequences

- Good: Frontend tidak perlu mengetahui locale tanggal; cukup render
  apa yang dikirim server.
- Good: Tanggal kosong atau malformed sort ke bawah (parser
  mengembalikan `(0, 0, 0)`), sehingga tidak mengganggu posisi pasien
  dengan data valid.
- Good: Tiebreak `P003` di atas `P001` ketika dua pasien punya tanggal
  kunjungan yang sama (umumnya baru-baru ini didaftarkan terlebih
  dahulu di hari yang sama).
- Good: Mudah di-unit-test: input list pasien, harapan urutan.
- Bad: Parser tuple toleran berarti tanggal salah format tidak
  ditolak; validasi format kunjungan dilakukan terpisah saat create
  jika dibutuhkan.
- Bad: Sorting di-recompute setiap GET; untuk dataset kecil (faskes
  1) ini diterima, tetapi pada skala lebih besar memerlukan index.

### Confirmation

- Parser: `api/routes/patient_routes.py:30-45` mendefinisikan
  `_parse_visit_date(s) -> tuple[int, int, int]` yang split string
  DD-MM-YYYY menjadi `(y, m, d)`, mengembalikan `(0, 0, 0)` untuk
  string kosong atau malformed.
- Tiebreak: `api/routes/patient_routes.py:48-53` mendefinisikan
  `_id_num(pid)` yang mengekstrak tail numerik dari id seperti `P001
  -> 1`.
- List endpoint: `api/routes/patient_routes.py:135-146` melakukan
  `sorted(..., key=lambda p: (_parse_visit_date(...), _id_num(...)),
  reverse=True)` sebelum mengembalikan `_summary` per pasien.
- Komentar inline: `api/routes/patient_routes.py:139-141` menjelaskan
  "B07: newest visit first. Tiebreak by descending numeric patient id
  so P003 lists before P001 when both have the same kunjungan date."

## More Information

- ADR-0003 (skema canonical anggota2) memastikan ID `P001` yang
  digunakan oleh parser ini sesuai dengan format Bimo.
- Bug B07 didokumentasikan dalam `.mission/bugs.md`.
