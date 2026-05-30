# ADR-0002: JWT HS256 + bcrypt cost 12 + httpOnly cookie untuk autentikasi

- Status: accepted
- Date: 2026-05-18
- Deciders: Ghaisan Khoirul Badruzaman (Project Leader, 251524048), Abhidal Muhammad Gazza (UI/UX, 251524032)

## Context and Problem Statement

MedWatch perlu mekanisme login yang resilien terhadap XSS, mudah
di-deploy gratis di Cloud Run, dan tidak memperluas permukaan serangan
dengan flow yang kompleks (misal refresh token rotation, OAuth eksternal).
Anggota5 awal hanya menyimpan password plaintext per pengguna (lihat
`anggota5/data/users.json` versi awal); ini tidak dapat diterima sebagai
basis untuk presentasi yang dilihat dosen.

## Decision Drivers

- Tidak ada paid identity provider (kontrak free-tier project).
- Password tidak boleh disimpan dalam bentuk plaintext atau hash cepat.
- JWT tidak boleh dapat dibaca JavaScript klien.
- Sesi cukup pendek untuk membatasi dampak token hijack dan cukup
  panjang untuk demo dosen (tidak perlu re-login per 10 menit).
- Kompleksitas minimum: tanpa refresh token, tanpa key rotation
  selama window submission.

## Considered Options

- Session opaque + tabel sesi server-side.
- JWT HS256 dengan secret tunggal di Secret Manager, cookie httpOnly,
  expiry 12 jam.
- JWT RS256 dengan key pair + JWKS endpoint.
- OAuth 2.0 via Google.

## Decision Outcome

Chosen option: "JWT HS256 + bcrypt cost 12 + httpOnly cookie", karena
memberikan keamanan yang sesuai untuk deliverable akademis sambil
menjaga arsitektur tetap sederhana, gratis, dan dapat diaudit dalam
satu sweep OWASP.

### Consequences

- Good: Tidak ada state sesi server-side; backend Cloud Run benar-benar
  stateless dan dapat di-scale ke nol antar permintaan.
- Good: Bcrypt cost 12 (default) memperlambat brute-force kredensial
  curian; pada laptop developer biasa, satu verify membutuhkan ratusan
  milidetik.
- Good: Atribut cookie `httpOnly + Secure + SameSite=Lax`
  mengeliminasi vektor XSS langsung dan mengurangi risiko CSRF.
- Good: Klaim minimal (`sub, role, name, iat, exp, iss`) menjaga
  ukuran token tetap kecil dan menyederhanakan validasi.
- Bad: Tidak ada refresh token, jadi sesi yang sudah dikeluarkan tidak
  dapat dicabut sebelum `exp` tanpa rotasi `JWT_SECRET`.
- Bad: HS256 menggunakan secret simetris; siapa pun yang dapat membaca
  Secret Manager dapat memalsukan token. Mitigasi: secret dibatasi
  hanya untuk service account Cloud Run dengan role Secret Accessor
  yang ketat.

### Confirmation

- Hashing: `api/auth.py:11-12` menggunakan `bcrypt.hashpw(...,
  bcrypt.gensalt(rounds=12))` dan `api/auth.py:15-19` memverifikasi
  via `bcrypt.checkpw`.
- Issuance: `api/auth.py:22-32` memasukkan klaim `sub, role, name,
  iat, exp, iss="medwatch-api"` dan menandatangani dengan
  `JWT_ALGORITHM` (HS256) plus secret dari `api/config.py`.
- Verification: `api/auth.py:35-39` memverifikasi `iss` dan algoritma
  saat decoding.
- Login endpoint: `api/routes/auth_routes.py:13-40` melakukan flow
  end-to-end (load user, verify_password, issue_token, return JSON).
- Cookie set: `src/app/api/[...slug]/route.ts:82-89` set cookie
  `medwatch_token` dengan `httpOnly: true`, `secure: process.env.NODE_ENV
  === "production"`, `sameSite: "lax"`, `maxAge: 12 * 60 * 60`.

## More Information

- ADR-0001 menjelaskan kenapa cookie ini disimpan oleh proxy Vercel
  alih-alih oleh backend Flask.
- Threat model lengkap untuk token dan PII pasien akan ditulis di
  `docs/SECURITY.md` (W2-D10).
