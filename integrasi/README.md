# integrasi/ — Merge Handler Desktop CLI

Folder ini adalah merge layer yang nge-compose modul `anggota1` sampai `anggota5` jadi satu desktop CLI app dengan login + role-based menu. Implementasi target tim "merge masing-masing modul" tanpa modify file anggota satu pun.

## Quick start

Dari root repo `medWatch/`:

```bash
python integrasi/app_terpadu.py
```

## Demo credentials (dari anggota5/data/users.json)

| Role | Username | Password |
|---|---|---|
| Admin | `admin1` | `admin123` |
| Tenaga Kesehatan | `bidan1` | `bidan123` |

## Menu per role

**Admin:**
1. Scraper data obat (anggota1)
2. CRUD tenaga kesehatan (anggota5/tkesehatan_crud)
3. CRUD data pasien (anggota2)
4. Pencarian obat & safety check (anggota4)
5. Visualisasi grafik (anggota3)
6. Ekspor laporan PDF (anggota5)

**Tenaga Kesehatan:**
1. CRUD data pasien (anggota2)
2. Pencarian obat & safety check (anggota4)
3. Visualisasi grafik (anggota3)
4. Ekspor laporan PDF (anggota5)

## Arsitektur

- `app_terpadu.py` — entry point, panggil login dari anggota5/auth.py terus dispatch menu sesuai role
- `adapter.py` — shim functions untuk panggil tiap modul anggota via subprocess atau import langsung
- `__init__.py` — package marker

## Catatan

- Modul `anggota1`-`anggota5` tidak diubah. Adapter cuma orchestrate.
- Login pakai akun dari `anggota5/data/users.json` (role-based per Abhidal's revision).
- Untuk web version dari fitur yang sama, lihat folder `api/` (Flask + Cloud Run + Vercel frontend).
