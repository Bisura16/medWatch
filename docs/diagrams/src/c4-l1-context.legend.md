# Legenda Notasi C4 Level 1 - System Context

Diagram ini menggunakan notasi C4 (Brown, https://c4model.com) tingkat 1: System Context.

## Bentuk
- **Person** - aktor manusia (tenaga_kesehatan, masyarakat, admin).
- **System** (warna biru) - sistem yang sedang dibahas, yaitu MedWatch.
- **System_Ext** (warna abu) - sistem eksternal di luar kendali tim: openFDA API dan GCP Secret Manager.

## Garis hubung
- **Solid arrow** dengan label teknologi atau protokol = hubungan runtime.
- Label berisi *what* (deskripsi aksi) + *how* (protokol seperti HTTPS atau gRPC/IAM).

## Boundary
Level 1 tidak menggambar boundary internal karena hanya satu sistem yang dibahas. Level 2 (`c4-l2-container.mmd`) memecah sistem MedWatch menjadi container.

## Sumber data
- Tiga peran pengguna berasal dari `api/data/users.json` schema dan didefinisikan dalam konvensi proyek.
- openFDA endpoint berasal dari `anggota1/openfda/fetch.py`.
- Secret Manager dipakai backend Cloud Run via IAM (lihat `docs/SECURITY.md`).
