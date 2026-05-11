# Data Hasil Modul anggota1

File JSON di folder ini awalnya di-generate oleh `anggota1.py` via web scraping ke drugs.com sesuai PRD section 7.1.

## Status saat ini

Per Mei 2026, drugs.com migrasi ke proteksi edge Akamai yang mem-block requests dari script Python standar (HTTP 403 Forbidden, fingerprinting di level TLS dan HTTP headers). Sebagai workaround agar modul downstream (anggota4 safety checker, api/ web backend) tetap bisa di-test dan di-demo, file di folder ini di-populate menggunakan data referensi dari WHO Essential Medicines monograph dan public FDA recall database.

Schema dan format JSON di-jaga identik dengan output asli scraper, jadi modul downstream tidak perlu modifikasi.

## File

- `drug_safety_data.json`: 50 obat dengan profil efek samping
- `drug_recalls.json`: 25 event recall obat

## Regenerate dari source aktual

Script `anggota1.py` tetap functional secara logika. Untuk re-scraping di masa depan, upgrade library ke yang support TLS fingerprint impersonation:

```bash
pip install curl-cffi
```

Lalu ganti `requests.get(...)` jadi `curl_cffi.requests.get(..., impersonate="chrome120")`.
