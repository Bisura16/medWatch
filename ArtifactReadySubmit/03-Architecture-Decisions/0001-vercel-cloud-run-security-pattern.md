# ADR-0001: Vercel Next.js + Cloud Run Flask dengan security pattern B (server-side proxy)

- Status: accepted
- Date: 2026-05-18
- Deciders: Ghaisan Khoirul Badruzaman (Project Leader, 251524048)

## Context and Problem Statement

Aplikasi MedWatch perlu memisahkan presentasi web (Next.js + Vercel)
dari layanan backend Python Flask (Cloud Run) tanpa membocorkan URL
backend ke browser atau menyimpan JWT di tempat yang dapat dibaca
JavaScript. Sebuah klien browser yang memegang JWT dalam `localStorage`
rentan terhadap XSS; sebuah klien yang memanggil URL Cloud Run secara
langsung mengikat frontend ke detail deployment dan memunculkan CORS
preflight per panggilan.

## Decision Drivers

- Pertahankan satu origin yang dilihat browser (`*.vercel.app`) sehingga
  cookie httpOnly tetap valid.
- Tutup detail deployment backend (URL Cloud Run dapat berubah).
- Kurangi CORS preflight pada setiap permintaan otentikasi.
- Resilien terhadap XSS: token tidak boleh dapat diakses oleh skrip
  pada halaman.

## Considered Options

- Pattern A: browser memanggil Cloud Run langsung, JWT disimpan dalam
  `localStorage`, CORS allowlist ketat.
- Pattern B: browser hanya memanggil `*.vercel.app`, Next.js catch-all
  proxy meneruskan ke Cloud Run, JWT disimpan dalam httpOnly cookie.
- Pattern C: container monolitik (Flask serve Next.js build) pada
  Cloud Run.

## Decision Outcome

Chosen option: "Pattern B (server-side proxy)", karena memenuhi semua
decision driver sekaligus, tidak menambah biaya infrastruktur, dan
sejalan dengan kemampuan native Next.js Route Handlers di App Router.

### Consequences

- Good: JWT tidak terekspos ke JavaScript klien (httpOnly + Secure +
  SameSite=Lax) sehingga XSS yang berhasil tidak otomatis mendapat
  token sesi.
- Good: Permintaan selalu same-origin terhadap `*.vercel.app`, tidak
  ada preflight CORS untuk panggilan dari halaman frontend ke
  `/api/...`.
- Good: Backend dapat diganti tanpa men-deploy ulang frontend; cukup
  ubah environment variable `BACKEND_API_URL` di Vercel.
- Good: Edge Routing Middleware (`src/proxy.ts`) dapat memvalidasi
  token dan melakukan redirect role-based sebelum permintaan mencapai
  Cloud Run.
- Bad: Setiap panggilan terkena hop tambahan Vercel -> Cloud Run yang
  menambah latensi belasan milidetik.
- Bad: Penggunaan bandwidth Vercel naik karena seluruh body bolak-balik
  melalui proxy.

### Confirmation

- Proxy catch-all: `src/app/api/[...slug]/route.ts:11` membaca
  `process.env.BACKEND_API_URL` server-side, `route.ts:29` merangkai
  URL ke backend, `route.ts:38-42` menyisipkan JWT dari cookie ke
  header `Authorization`, dan `route.ts:76-93` men-set cookie
  `medwatch_token` dengan flag `httpOnly`, `secure` (di production),
  `sameSite: "lax"`, dan `maxAge` 12 jam.
- Edge Routing Middleware: `src/proxy.ts:46-52` membaca cookie
  `medwatch_token` dan redirect ke `/login` jika kosong; `proxy.ts:22-33`
  mendekode payload JWT untuk role-based routing; `proxy.ts:85-89`
  matcher mengecualikan path internal Next.js.
- Login endpoint backend: `api/routes/auth_routes.py:13-40` menerima
  username + password, memverifikasi via `verify_password`, dan
  mengembalikan JWT (yang lalu di-set sebagai cookie oleh proxy).

## More Information

- .md Section "Frontend <-> Backend correlation pattern" memuat
  pola arsitektur yang sama dan menjadi rujukan tim.
- ADR-0002 melengkapi keputusan ini dengan pemilihan algoritma JWT,
  bcrypt cost, dan atribut cookie.
- `api/SECURITY_AUDIT.md` mencatat hasil sweep OWASP atas keputusan ini.
