# medWatch

---

## Integration Layer: `api/` (added by Ghaisan, branch `ghaisan-APIIntegration`)

> Section ini ditambahkan oleh Ghaisan Khoirul Badruzaman di branch `ghaisan-APIIntegration`. Modul anggota1-5 tidak diubah. Section di atas garis ini tetap milik Bimo (asli).

Folder `api/` di root repo ini adalah integration layer Flask yang membungkus modul anggota1-5 menjadi REST endpoints, dideploy ke GCP Cloud Run, dan dikoneksikan ke frontend Next.js di Vercel.

- **API code:** [`./api/`](./api/)
- **API documentation:** [`./api/README.md`](./api/README.md)
- **Architecture diagrams:** [`./docs/diagrams/`](./docs/diagrams/) (18 diagrams: drawio source + PNG)
- **Integration guide:** [`./docs/INTEGRATION_GUIDE.md`](./docs/INTEGRATION_GUIDE.md)
- **Scope note for lecturer:** [`./docs/SCOPE_NOTE.md`](./docs/SCOPE_NOTE.md)
- **Security audit:** [`./docs/SECURITY_AUDIT.md`](./docs/SECURITY_AUDIT.md)
- **Live backend:** https://medwatch-api-517694123086.asia-southeast1.run.app
- **Live frontend:** https://medwatch-frontend.vercel.app

## Merge layer: `integrasi/`

Folder `integrasi/` adalah desktop CLI app yang nge-compose anggota1-5 jadi satu entry point dengan role-based menu. Implementasi target tim "merge masing-masing modul" tanpa modify file anggota satu pun.

```bash
python integrasi/app_terpadu.py
# Login: admin1 / admin123  (admin)
# Login: bidan1 / bidan123  (tenaga_kesehatan)
```

Lihat [`./integrasi/README.md`](./integrasi/README.md) untuk detail.

## Quick start backend (web layer)

```bash
cd api
pip install -r requirements.txt
JWT_SECRET=dev-only python -m flask --app api.app run --port 8080
# visit http://localhost:8080/ for endpoint docs
```

Lihat [`./api/README.md`](./api/README.md) untuk endpoint reference, demo credentials, dan deployment commands.
