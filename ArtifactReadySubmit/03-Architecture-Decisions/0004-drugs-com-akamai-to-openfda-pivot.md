# ADR-0004: Pivot dari drugs.com (Akamai HTTP 403) ke openFDA REST API

- Status: accepted
- Date: 2026-05-18
- Deciders: Ghaisan Khoirul Badruzaman (Project Leader, 251524048)

## Context and Problem Statement

Modul scraping awal `anggota1/anggota1.py` mengandalkan parsing HTML
drugs.com untuk dua dataset utama (efek samping per obat dan recall
obat). Pada Mei 2026 setiap request HTTP dari modul tersebut dibalas
oleh proteksi anti-bot Akamai dengan status 403, sehingga jumlah baris
yang berhasil di-scrape menjadi nol untuk kedua dataset. Mission ini
membutuhkan dataset real dengan skala besar (>= 5000 baris recall) dan
tidak boleh melakukan bypass anti-bot.

## Decision Drivers

- Tidak boleh melakukan teknik bypass anti-bot (CAPTCHA solver,
  rotating residential proxy, browser fingerprint spoofing): melanggar
  ToS drugs.com dan etika riset (lihat aturan mission section 6 dan
  CLAUDE.md "All resources must be free").
- Modul `anggota1.py` tetap milik Ghaisan namun di-treat sebagai
  read-only dalam mission ini agar kontrak tidak bercabang.
- Output schema harus tetap kompatibel dengan downstream consumer
  (anggota3 visualisasi, anggota4 safety checker, backend `api/`,
  frontend) tanpa modifikasi.
- Sumber data resmi yang gratis, dapat diaudit, dan tidak menyimpan PII
  pasien.

## Considered Options

- Bypass Akamai dengan residential proxy + headless browser.
- Pivot ke openFDA REST API (FAERS untuk adverse events,
  Enforcement Reports untuk recalls).
- Gunakan dataset BPOM Indonesia langsung (RDF/CSV publik).
- Tunda data real, sajikan data dummy.

## Decision Outcome

Chosen option: "openFDA REST API", karena merupakan satu-satunya
sumber gratis, legal, dan lengkap yang cocok untuk kedua dataset yang
dibutuhkan (efek samping per obat dan recall obat) dan secara eksplisit
disetujui dalam constraint mission section 6: "openFDA adalah API data
obat eksternal yang disanksi."

### Consequences

- Good: Data real dengan skala besar berhasil diperoleh. Pengukuran
  pada repo saat ADR ini ditulis: 74 obat dengan 1850 entri efek
  samping di `anggota1/data/drug_safety_data.json` (2517 baris JSON
  terformat) dan 6000 record recall di
  `anggota1/data/drug_recalls.json` (42001 baris JSON terformat).
- Good: Endpoint openFDA mengembalikan data yang sudah
  de-identified oleh FDA (tidak ada PII pasien), sesuai dengan
  preferensi privasi mission.
- Good: API key openFDA gratis memberikan kuota 120000 request per
  24 jam (vs 1000 tanpa key); cukup untuk regenerasi penuh dengan
  margin yang besar.
- Good: Modul `anggota1.py` lama tetap utuh; modul baru ditulis
  sebagai sibling tambahan `anggota1/openfda/`.
- Bad: Skema field di openFDA berbeda dengan drugs.com, memerlukan
  fungsi mapping di sisi acquisition (severity bucket diturunkan dari
  fraksi `serious` dan `seriousnessdeath`).
- Bad: openFDA tidak mengembalikan teks Bahasa Indonesia; nama efek
  samping berbahasa Inggris MedDRA. Lapisan tampilan
  bertanggung jawab atas translasi atau tetap menampilkan istilah
  klinis aslinya.

### Confirmation

Bukti verbatim dari `anggota1/scraper.log` (eksekusi 11 Mei 2026 versi
modul lama; status code drugs.com pada setiap request adalah HTTP 403):

```
[1/2] scraping efek samping (64 obat)
  [1/64] ibuprofen
    status 403
  [2/64] paracetamol
    status 403
  [3/64] aspirin
    status 403
  [4/64] naproxen
    status 403
  [5/64] diclofenac
    status 403
```

Dan pada bagian recall di file yang sama:

```
[2/2] scraping recall obat
  halaman 1
    status 403
  -> /Users/ghaisan/Documents/MedWatchIntegration/medWatch/anggota1/data/drug_recalls.json (0 baris)

selesai. safety=0 baris, recalls=0 baris
```

Baris penutup `selesai. safety=0 baris, recalls=0 baris` menjadi sinyal
bahwa modul lama tidak menghasilkan data, sehingga pivot dilakukan.

- Endpoint pengganti: `anggota1/openfda/fetch.py:56-57` mendefinisikan
  `EVENT_ENDPOINT = "https://api.fda.gov/drug/event.json"` dan
  `ENFORCEMENT_ENDPOINT = "https://api.fda.gov/drug/enforcement.json"`.
- Penanganan API key: `anggota1/openfda/fetch.py:18-21` membaca
  `OPENFDA_API_KEY` dari environment dan mengirimnya hanya sebagai
  query parameter `api_key`; nilai tidak pernah dicetak, dilog, atau
  ditulis ke disk.
- Severity bucket: `anggota1/openfda/README.md:60-66` mendefinisikan
  threshold `serius / sedang / ringan` berdasarkan fraksi laporan serius
  dan kematian.
- Skema output tetap identik dengan modul lama:
  `anggota1/openfda/README.md:42-77` mendokumentasikan field
  `drug_name, category, side_effects[], severity_level, warnings,
  source_url` untuk safety data dan `product_name, reason, recall_date,
  severity_class, company` untuk recalls.
- Perintah regenerasi: dari root repo,
  `OPENFDA_API_KEY=<your-key> .venv/bin/python -m anggota1.openfda.fetch`
  (lihat `anggota1/openfda/README.md:85-87`).

## More Information

- `anggota1/openfda/README.md:122-135` mengutip baris awal scraper.log
  yang sama untuk konteks tim.
- Sumber data, ToS openFDA, dan basis legal pivot ada di section
  "Dasar legal" pada `anggota1/openfda/README.md:113-119`.
- Bypass anti-bot tidak dipertimbangkan kembali dalam ADR ini atau di
  mana pun dalam mission; setiap usulan ke arah itu harus dimulai
  dari ADR baru yang secara eksplisit men-supersede ADR-0004.
