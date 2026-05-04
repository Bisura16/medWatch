# MedWatch Scope Note for Lecturer Discussion

This is a one-page handout for Bu Aprianti, Pak Ade, atau Pak Ardhian if questions about scope expansion arise during the presentation.

## Original PRD scope (semester 2 2025/2026)

The MedWatch PRD (`MedWatch_PRD.pdf` in repo root) explicitly lists as **out of scope** in section 5.2:
- "Fitur login atau multi-user dengan autentikasi"
- "Deployment ke platform web atau mobile"

The PRD primary deliverable is the **modular CustomTkinter desktop application** composed from anggota1 through anggota5, run from `python main.py` (CLI tester) and `python integrasi/app_terpadu.py` (unified merge). This deliverable is intact and unchanged.

## What was added (presentation supplement)

To demonstrate system integration concepts beyond the minimum PRD requirements, the team added a supplementary web stack:

- **Web frontend** (Next.js 16 + TypeScript + Tailwind v4 on Vercel): https://medwatch-frontend.vercel.app
- **REST API layer** (Flask + JWT + bcrypt on GCP Cloud Run): https://medwatch-api-517694123086.asia-southeast1.run.app
- **3-role authentication** (`tenaga_kesehatan`, `masyarakat`, `admin`)
- **Cloud Storage persistence** for users + patients
- **Secret Manager** for JWT signing key

This stack is **a polish layer over the existing modular design**, not a replacement for the desktop deliverable. The api/ folder wraps modul anggota1-5 (read-only). Modul anggota1-5 themselves remain modular CustomTkinter / CLI per PRD.

## Why added (rationale)

1. **Demonstrate System Integration concepts.** The PPL Desktop course emphasizes modularity. The web stack shows the same modular principle applied at a different abstraction level (REST endpoints instead of imports).
2. **Demonstrate Cloud / DevOps concepts.** GCP Cloud Run, Cloud Storage, Secret Manager, IAM, CI/CD via gcloud all illustrate production-grade deployment patterns relevant to industry.
3. **Demonstrate Security concepts.** JWT auth, bcrypt password hashing, role-based access control, OWASP Top 10 review (`docs/SECURITY_AUDIT.md`) demonstrate security thinking beyond the minimum.
4. **Provides a memorable demo surface.** A clickable web demo at `medwatch-frontend.vercel.app` is more accessible to non-technical stakeholders than a CLI desktop app.

## Where the desktop modules live

All modular code per PRD remains untouched:
- `anggota1/anggota1.py` — Ghaisan, scraper drugs.com + FDA
- `anggota2/PasienCRUD.py` (and submodules) — Bimo, CRUD pasien SOAP
- `anggota3/TampilGrafik.py` (and submodules) — Alia, visualisasi matplotlib
- `anggota4/safety_checker.py` (and submodules) — Iqbal, drug safety check
- `anggota5/main_anggota5.py` (and submodules) — Abhidal, PDF export + role-based auth

The merge layer at `integrasi/app_terpadu.py` composes them into a unified CLI app per the team's "merge masing-masing modul" weekly target.

## What is NOT in this supplement

- Mobile app (still out of scope)
- Patient self-service signup (admin-only user provisioning per Abhidal's revision)
- HIPAA/PHI compliance (this is a presentation demo with synthetic data)
- Production-grade observability beyond Cloud Logging
- Custom domain (default `.run.app` and `.vercel.app` URLs only)

## Cost

Entire web supplement runs within the GCP free trial credit ($300 attached to Ghaisan's billing account `ghaisan.khoirul.b@gmail.com`). Vercel uses Hobby tier (free). No paid third-party services. Total ongoing cost after free trial: estimated < $5/month at zero traffic, scales with usage.

## Authorship of supplement

The web supplement (api/, integrasi/, docs/, frontend integration) is authored by Ghaisan Khoirul Badruzaman (Project Leader / Team Coordinator, NIM 251524048) as personal integration work. Abhidal's anggota5 revision (role-based auth, removal of public signup) was committed with his explicit authorization via WhatsApp group request, with attribution clearly documented in the commit message.

No teammate's anggota1-4 code was modified.

## Bottom line

The desktop modular deliverable is the primary submission per PRD. The web stack is a supplementary demo layer that demonstrates additional concepts without replacing or compromising the original scope.
