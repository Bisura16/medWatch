# ADR-0010: Submit login membaca username dan password dari FormData untuk mencegah autofill race

- Status: accepted
- Date: 2026-05-18
- Deciders: Ghaisan Khoirul Badruzaman (Project Leader, 251524048)

## Context and Problem Statement

Bug register entry B09 melaporkan dua gejala terkait login:
(1) Ketika pengguna mengetik username dan password secara manual,
kemudian menekan tombol login dengan cepat, request kadang terkirim
dengan field kosong (login gagal 401). (2) Demo credential preset
(`bidan_siti`, `umum_budi`, `admin_ghaisan`) tidak terlihat di
halaman login. Investigasi Iterasi 1 menemukan penyebab gejala pertama:
state React `username` dan `password` mungkin belum sinkron dengan
nilai input DOM saat handler `submit` dieksekusi, terutama setelah
password manager autofill atau setelah klik preset yang menulis nilai
ke input secara terprogram.

## Decision Drivers

- Submit harus mengirim nilai input yang persis terlihat oleh pengguna,
  bukan snapshot state React yang mungkin tertinggal.
- Tidak boleh mengabaikan password manager / autofill flow.
- Tetap memakai controlled input untuk UX (validation real-time,
  preset prefill, kunci capslock).
- Logika tetap berada di komponen client tanpa harus mengintroduksi
  ref ke setiap input.

## Considered Options

- Tetap memakai state React `username/password` saja (status quo,
  reproduksi bug).
- Tambahkan `setTimeout(0)` sebelum submit untuk memberi React sempat
  flush.
- Baca nilai langsung dari `FormData(form)` di dalam handler submit;
  fallback ke state React jika FormData kosong.
- Beralih ke uncontrolled input penuh dengan ref.

## Decision Outcome

Chosen option: "Baca dari `FormData(form)` di handler submit, fallback
ke state React", karena bersifat zero-risk terhadap UX yang ada,
selalu mengambil nilai input visual terkini, dan tetap berfungsi pada
seluruh browser modern tanpa polyfill.

### Consequences

- Good: Submit selalu mengirim nilai input yang terlihat pengguna,
  mengeliminasi window race condition antara autofill dan state React.
- Good: Tidak ada perubahan ke layout JSX; hanya beberapa baris di
  handler.
- Good: Preset demo (klik tombol "Demo Bidan" dsb.) tetap mengisi
  state React, tetapi submit-nya tidak tergantung pada propagasi
  state.
- Good: Demo credential preset visual ditampilkan sebagai tombol di
  bawah form, mengatasi gejala kedua B09 (visibility).
- Bad: Logika handler sedikit lebih panjang; dokumentasi inline wajib
  untuk menjelaskan kenapa.
- Bad: Jika di masa depan input tidak memiliki atribut `name=`,
  FormData tidak akan mengambilnya; perlu lint atau test kecil yang
  menjaga atribut `name` tetap ada.

### Confirmation

- Komentar inline yang menjelaskan alasan:
  `src/app/login/page.tsx:85-89` "Read straight from the DOM via
  FormData so that browser autofill, password managers, or
  controlled-input race conditions cannot leave submit firing with
  stale empty React state. The visible input values are always the
  source of truth on submit."
- Implementasi: `src/app/login/page.tsx:90-92` `const fd = new
  FormData(form); const u = (fd.get("username") as string | null)
  ?.trim() || username.trim(); const p = (fd.get("password") as
  string | null) || password;`.
- Preset visibility: `src/app/login/page.tsx:18-43` mendefinisikan
  tiga preset (`bidan_siti / siti2026 -> tenaga_kesehatan`,
  `umum_budi / budi2026 -> masyarakat`, `admin_ghaisan / admin2026
  -> admin`) dengan label, color, dan role.

## More Information

- ADR-0002 mencatat klaim JWT yang dihasilkan oleh login endpoint
  yang dipanggil dari handler ini.
- ADR-0001 mencatat alur cookie set yang terjadi di proxy setelah
  endpoint login mengembalikan token.
- Bug B09 didokumentasikan dalam catatan internal proyek.
