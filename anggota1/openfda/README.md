# anggota1/openfda

Modul real large-scale data acquisition untuk MedWatch (W1-DATA).

Module ini dibuat sebagai pengganti aditif untuk `anggota1/anggota1.py`
setelah drugs.com memasang proteksi Akamai yang memblokir setiap request
dengan HTTP 403 (lihat `anggota1/scraper.log`). File `anggota1.py` tetap
read-only sesuai kontrak tim. Output JSON ditulis ke folder yang sama
(`anggota1/data/`) dengan schema yang sama persis, sehingga semua
consumer downstream (anggota4 safety checker, anggota3 visualisasi,
backend `api/`, frontend) tetap bekerja tanpa modifikasi.

## Sumber data

| Endpoint | Kegunaan | Field utama |
|---|---|---|
| `https://api.fda.gov/drug/event.json` | Adverse Event Reporting System (FAERS). | `patient.reaction.reactionmeddrapt`, `serious`, `seriousnessdeath`, `patient.drug.medicinalproduct` |
| `https://api.fda.gov/drug/enforcement.json` | FDA Recall / Enforcement Reports. | `product_description`, `reason_for_recall`, `recall_initiation_date`, `classification`, `recalling_firm` |

Dokumentasi openFDA: https://open.fda.gov/apis/drug/event/ dan
https://open.fda.gov/apis/drug/enforcement/.

## Otentikasi dan rate limit

- API key dibaca dari environment variable `OPENFDA_API_KEY`. Value
  tidak pernah di-print, di-log, di-commit, atau ditulis ke disk.
  Dalam log dan `source_url` di output JSON, value diganti placeholder
  `<redacted>`.
- Dengan API key: 240 request per menit dan 120.000 request per 24 jam
  per IP.
- Tanpa API key: 240 request per menit dan 1.000 request per 24 jam.
- Polite delay 250 ms antar request.
- Exponential backoff dengan jitter pada HTTP 429 dan 5xx, maksimum 5
  retry.
- HTTP 404 dianggap "no data" (drug tidak ada di FAERS), modul skip dan
  lanjut ke obat berikutnya.

## Mapping schema

### `drug_safety_data.json`

```jsonc
{
  "drug_name":      "Paracetamol",
  "category":       "Analgesik",
  "side_effects":   ["Vomiting", "Nausea", ...],   // top 25 dari count=patient.reaction.reactionmeddrapt.exact
  "severity_level": "ringan | sedang | serius",     // diturunkan dari fraksi laporan serius + fatal
  "warnings":       "Berdasarkan N laporan FAERS ...",
  "source_url":     "https://api.fda.gov/drug/event.json?...&api_key=<redacted>"
}
```

Severity diturunkan dari dua sinyal FAERS:

- `serious_fraction` = jumlah laporan dengan `serious=1` dibagi total
  laporan yang mengisi field tersebut.
- `death_fraction` = jumlah laporan dengan `seriousnessdeath=1` dibagi
  total laporan untuk obat tersebut.

Threshold:

| Bucket | Kondisi |
|---|---|
| `serius` | `death_fraction > 5%` ATAU `serious_fraction >= 70%` |
| `sedang` | `serious_fraction >= 30%` |
| `ringan` | sisanya |

### `drug_recalls.json`

```jsonc
{
  "product_name":   "...",                  // dari product_description, dipotong 240 char
  "reason":         "...",                  // dari reason_for_recall, dipotong 500 char
  "recall_date":    "YYYY-MM-DD",           // recall_initiation_date dikonversi dari YYYYMMDD ke ISO
  "severity_class": "Class I | Class II | Class III | Not Yet Classified",
  "company":        "..."                   // dari recalling_firm
}
```

## Cara menjalankan

Prasyarat: Python 3.11+, `requests` terpasang.

```bash
# dari root repo medWatch
export OPENFDA_API_KEY=<your-key-here>
.venv/bin/python -m anggota1.openfda.fetch --max-recall-pages 6
```

CLI flag yang tersedia:

| Flag | Default | Keterangan |
|---|---|---|
| `--drugs FILE` | bundled list 74 obat | File newline-separated nama obat untuk pull FAERS. |
| `--max-drugs N` | `0` (no cap) | Cap jumlah obat yang di-query. |
| `--max-recall-pages N` | `26` | Maksimum halaman recall (1 halaman = 1000 record). |
| `--skip-events` | off | Skip pull FAERS. |
| `--skip-recalls` | off | Skip pull recall. |
| `--log-level` | `INFO` | Python logging level. |

Contoh:

```bash
# pull recall saja, sampai habis (target >= 5000 record)
.venv/bin/python -m anggota1.openfda.fetch --skip-events --max-recall-pages 26

# pull 10 obat populer Indonesia saja
echo -e "paracetamol\namoxicillin\nibuprofen\n..." > my_drugs.txt
.venv/bin/python -m anggota1.openfda.fetch --drugs my_drugs.txt --skip-recalls
```

## Dasar legal

openFDA adalah layanan publik gratis yang dioperasikan oleh U.S. Food
and Drug Administration. Lihat https://open.fda.gov/apis/ Terms of
Service: penggunaan programmatic dengan API key diizinkan untuk
penelitian, integrasi, dan publikasi. Data hasil FAERS tidak
mengandung PII pasien (sudah de-identified oleh FDA sebelum
dipublikasikan).

## Riwayat masalah drugs.com

Modul lama `anggota1/anggota1.py` mengandalkan scraping HTML dari
drugs.com. Per Mei 2026 setiap URL di-block oleh Akamai dengan HTTP
403 (lihat `anggota1/scraper.log`, kutip 3 baris pertama):

```
[1/2] scraping efek samping (64 obat)
  [1/64] ibuprofen
    status 403
```

Bypass anti-bot tidak dilakukan karena bertentangan dengan ToS
drugs.com dan etika riset. Modul openFDA ini adalah penggantian
legal.
