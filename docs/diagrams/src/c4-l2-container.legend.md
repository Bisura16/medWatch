# Legenda Notasi C4 Level 2 - Container

Diagram ini menggunakan notasi C4 tingkat 2: Container.

## Bentuk
- **Container** - unit deploy terpisah (proses, browser, dll).
- **ContainerDb** - data store (GCS bucket atau filesystem JSON).
- **System_Boundary** - kotak besar yang membatasi sistem MedWatch.
- **Person** - aktor manusia.
- **System_Ext** - sistem eksternal (openFDA, Secret Manager).

## Garis hubung
Setiap garis hubung mencantumkan teknologi atau protokol (HTTPS same-origin, Bearer JWT, GCS JSON SDK, gRPC/IAM).

## Sumber file
- Frontend Next.js: `FrontendMedWatch/src/app/**`
- Proxy: `FrontendMedWatch/src/middleware/proxy.ts`
- Backend Flask: `api/app.py` + `api/routes/*.py`
- State bucket: `medwatch-polban-2026-state`
- Seed data: `anggota1/data/`, `anggota4/data/`
