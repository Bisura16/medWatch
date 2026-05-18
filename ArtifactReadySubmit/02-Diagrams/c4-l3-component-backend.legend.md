# Legenda Notasi C4 Level 3 - Component (Backend api/)

Diagram ini menggunakan notasi C4 tingkat 3: Component, untuk container Backend Flask `api/`.

## Bentuk
- **Component** - modul kode atau berkas Python di dalam container backend.
- **Container_Boundary** - dua boundary: "Backend Flask api/" dan "Modul anggota (read-only)".
- **ContainerDb** - data store (GCS bucket atau `api/data/`).
- **System_Ext** - sistem eksternal (openFDA).

## Garis hubung
- Solid arrow dengan label = panggilan fungsi atau `register_blueprint`.
- Boundary "Modul anggota (read-only)" merepresentasikan aturan project: backend hanya menulis wrapper di `api/`, sedangkan modul anggota1..5 dibaca via dynamic import (`bootstrap.get_module`).

## Sumber kode (file:line)
- `api/app.py:27` - `create_app()` factory dan registrasi blueprint.
- `api/middleware.py:17` - `require_auth`, `:37` - `require_role`.
- `api/auth.py:11` - `hash_password` (bcrypt cost 12), `:22` - `issue_token`.
- `api/routes/patient_routes.py:135` - `list_patients` (sort DESC B07), `:162` - `create_patient` (validasi B03).
- `api/routes/safety_routes.py:16` - `safety_check` plus B05 `pasien_active_meds`.
- `api/routes/admin_routes.py:21` - `trigger_scrape`, `:106` - `system_stats` (B10).
