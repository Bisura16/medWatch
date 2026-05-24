# Wave 3 Frontend Bundler Findings

Mission: medwatch-windows-installers-2026-05-25
Subagent: frontend-bundler
Date: 2026-05-25
Host: macOS Darwin 25.3.0
Working dirs:
- Backend (mission home): /Users/ghaisan/Documents/MedWatchIntegration/medWatch
- Frontend (build target): /Users/ghaisan/Documents/MedWatchIntegration/FrontendMedwatch

All file:line citations are absolute. UNVERIFIED is used wherever a claim could not be confirmed in this session.

---

## 1. Frontend branch

- Branch name: `mission/installer-static-export`
- Status: local-only, never pushed, never merged
- Base: `main` at HEAD as of 2026-05-25
- Final SHA: `95f1428ae39cf6d5acbe686803424056b986482c`
- Working tree on branch: clean after commit

Pre-mission `medwatch-frontend.vercel.app` deployment is unaffected because `main` is untouched and this branch is never pushed.

---

## 2. next.config.ts diff

Before (/Users/ghaisan/Documents/MedWatchIntegration/FrontendMedwatch/next.config.ts):

```ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["react-force-graph-2d", "force-graph"],
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
```

After:

```ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  transpilePackages: ["react-force-graph-2d", "force-graph"],
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
```

`images.unoptimized: true` was already set so it did not need adding. `experimental.useCache` was never present so nothing to disable.

---

## 3. Audit confirmation (Wave 0 scout findings still hold)

Commands run, no key value ever printed:

```
grep -rEln "export const dynamic = ['\"]force-dynamic['\"]" src/app
  -> src/app/safety-checker/page.tsx
  -> src/app/drug-comparison/page.tsx
  -> src/app/login/page.tsx

grep -rEln "'use server'" src
  -> (no matches)

grep -rEln "from ['\"]next/server['\"]" src
  -> src/proxy.ts (removed in this wave)
  -> src/app/api/[...slug]/route.ts (removed in this wave)

ls src/app/api/
  -> [...slug]

ls src/proxy.ts
  -> src/proxy.ts
```

All three blockers from Wave 0 confirmed present, all three handled below.

---

## 4. Page-by-page modifications

| Path | Before | After | Reason |
|---|---|---|---|
| FrontendMedwatch/next.config.ts | no `output` field | `output: "export"` + `trailingSlash: true` | Required for static export |
| FrontendMedwatch/src/app/login/page.tsx | exports `dynamic = "force-dynamic"` line 19 | dynamic export removed; client-side `useSearchParams` already wrapped in Suspense | Suspense boundary already present, no SSR features used |
| FrontendMedwatch/src/app/safety-checker/page.tsx | exports `dynamic = "force-dynamic"` line 21 | dynamic export removed; Suspense boundary preserved | Same recipe as login |
| FrontendMedwatch/src/app/drug-comparison/page.tsx | exports `dynamic = "force-dynamic"` line 19 | dynamic export removed; Suspense boundary preserved | Same recipe |
| FrontendMedwatch/src/app/page.tsx | server component calling `redirect("/dashboard")` | `"use client"` page that reads the auth store via `useEffect` and `router.replace`s either to `/login` or to the role landing | `redirect()` from `next/navigation` is a server feature incompatible with static export |
| FrontendMedwatch/src/app/api/[...slug]/route.ts | catch-all Vercel proxy to Cloud Run, used `cookies()` and `next/server` | DELETED | Not bundlable under `output: "export"` and not needed in desktop mode (renderer talks to bundled Flask directly) |
| FrontendMedwatch/src/proxy.ts | edge runtime auth and role gate | DELETED | Edge middleware does not run under static export. Wave 5 must add a client-side role gate in `AppShell` if needed |
| FrontendMedwatch/src/app/patients/[id]/page.tsx | dynamic route segment using `useParams` | DELETED; moved to FrontendMedwatch/src/app/patients/edit/page.tsx using `useSearchParams("id")` instead | `dynamicParams: true` is rejected by `output: "export"`; `generateStaticParams() => []` plus `dynamicParams: false` would 404 every real id; query-param route is the cleanest static-friendly equivalent |
| FrontendMedwatch/src/app/patients/page.tsx | link `/patients/${selected.id}` | link `/patients/edit/?id=${encodeURIComponent(selected.id)}` | Caller update for new route shape |
| FrontendMedwatch/src/app/patients/new/page.tsx | redirect `/patients/${created.id}` | redirect `/patients/edit/?id=${encodeURIComponent(created.id)}` | Same caller update |
| FrontendMedwatch/src/lib/api.ts | hardcoded relative path in fetch | imports `apiUrl` from `./api-base` and wraps every fetch | Runtime port injection for Electron desktop variant |
| FrontendMedwatch/src/lib/auth-store.ts | three `fetch("/api/auth/...")` calls | three `fetch(apiUrl("/api/auth/..."))` calls | Same runtime port injection |
| FrontendMedwatch/src/lib/api-base.ts | (did not exist) | new file exposing `apiBase()` and `apiUrl(path)` reading `window.__MEDWATCH_BACKEND_PORT__` | Single chokepoint for desktop vs Vercel base URL resolution |

---

## 5. Fetch call sites migrated to apiUrl()

Found via `grep -rEn "fetch\\(" src` (excluding deleted files). Total: 5 sites in 2 files.

| File | Line (post-edit) | Before | After |
|---|---|---|---|
| FrontendMedwatch/src/lib/api.ts | 51 | `fetch(path.startsWith("/") ? path : ` + "`/${path}`" + `, init)` | `fetch(apiUrl(path), init)` |
| FrontendMedwatch/src/lib/api.ts | 91 | `fetch(path, { method: "POST", ... })` | `fetch(apiUrl(path), { method: "POST", ... })` |
| FrontendMedwatch/src/lib/auth-store.ts | 45 | `fetch("/api/auth/login", { ... })` | `fetch(apiUrl("/api/auth/login"), { ... })` |
| FrontendMedwatch/src/lib/auth-store.ts | 65 | `fetch("/api/auth/logout", { method: "POST" })` | `fetch(apiUrl("/api/auth/logout"), { method: "POST" })` |
| FrontendMedwatch/src/lib/auth-store.ts | 72 | `fetch("/api/auth/me")` | `fetch(apiUrl("/api/auth/me"))` |

Every other API call in the codebase flows through `api.get` / `api.post` / `api.put` / `api.delete` (in `src/lib/api.ts`) or `downloadBlob` (same file). Migrating the central wrapper is therefore equivalent to migrating every call site.

---

## 6. New file: src/lib/api-base.ts

Path: `/Users/ghaisan/Documents/MedWatchIntegration/FrontendMedwatch/src/lib/api-base.ts`.

Exports:
- `apiBase(): string` returns `http://127.0.0.1:<port>` when `window.__MEDWATCH_BACKEND_PORT__` is set, otherwise empty string so Vercel relative paths keep working.
- `apiUrl(path: string): string` joins the base with the supplied path.

Declares `Window.__MEDWATCH_BACKEND_PORT__` via TypeScript module augmentation. The Electron preload at Wave 5 will set this via `contextBridge.exposeInMainWorld`.

---

## 7. Deletions

- `src/app/api/[...slug]/route.ts` (Vercel-only Cloud Run proxy)
- `src/proxy.ts` (edge runtime auth gate)
- `src/app/patients/[id]/page.tsx` (replaced by `src/app/patients/edit/page.tsx`)

UNVERIFIED but expected for Wave 5: the deletion of `src/proxy.ts` means the static export has no edge-layer role gate. If the Electron variant needs server-side-equivalent enforcement (block masyarakat from `/admin/*`, push unauthenticated users to `/login`), a client-side guard should be added inside `src/components/shell/AppShell.tsx`. The backend already enforces role checks at the API layer, so this is defense-in-depth, not a hard security gap.

---

## 8. Build output

Command: `npm run build` in /Users/ghaisan/Documents/MedWatchIntegration/FrontendMedwatch.

Summary:
- Next.js 16.2.1 (Turbopack)
- Compiled successfully in 1.4s
- TypeScript clean in 4.0s
- Page data collected with 9 workers
- 21 routes generated, all marked Static (circle marker in the Next.js route table)

Routes generated (verbatim from build log):
```
/ , /_not-found, /admin/dashboard, /admin/scraper, /admin/users,
/dashboard, /dashboard/aktivitas, /drug-comparison, /drug-search,
/export, /export-pdf, /heatmap, /login, /pasien/profile, /patients,
/patients/edit, /patients/new, /safety-checker, /visualization
```

The `out/` directory was produced at `/Users/ghaisan/Documents/MedWatchIntegration/FrontendMedwatch/out/` and is 2.6 MB on disk.

---

## 9. Static-server smoke test

Command: `cd out && python3 -m http.server 5500` then curl each URL with `-o /dev/null -w "%{http_code}"`. All requests received HTTP 200.

| URL | HTTP code |
|---|---|
| http://localhost:5500/ | 200 |
| http://localhost:5500/login/ | 200 |
| http://localhost:5500/safety-checker/ | 200 |
| http://localhost:5500/drug-comparison/ | 200 |
| http://localhost:5500/patients/edit/ | 200 |
| http://localhost:5500/dashboard/ | 200 |

Server was killed after the probe. Log captured at /tmp/static-server.log (one access line per probe, all 200).

---

## 10. Copy to both variant resources/renderer/

Commands run:

```
cp -R /Users/ghaisan/Documents/MedWatchIntegration/FrontendMedwatch/out/. \
  '/Users/ghaisan/Documents/MedWatchIntegration/medWatch/installer-based app/resources/renderer/'

cp -R /Users/ghaisan/Documents/MedWatchIntegration/FrontendMedwatch/out/. \
  '/Users/ghaisan/Documents/MedWatchIntegration/medWatch/portable-app/resources/renderer/'
```

Post-copy size (du -sh):
- `installer-based app/resources/renderer/`: 2.5M
- `portable-app/resources/renderer/`: 2.5M

Byte-identical verification: `diff -r` between the two directories produced zero output and exit code 0.

Top-level entries in each renderer/ (truncated to 20):
```
404 404.html __next.__PAGE__.txt __next._full.txt __next._head.txt
__next._index.txt __next._tree.txt _next _not-found admin dashboard
drug-comparison drug-search export export-pdf favicon.ico heatmap
index.html index.txt indonesia-provinces.json
```

---

## 11. UNVERIFIED items

1. The renderer was not loaded inside a real Electron BrowserWindow in this wave; the static-server smoke test is a closely related signal (same file:// vs http:// distinction handled by the same code path), but the actual `app://`/`file://` round-trip will be verified in Wave 5.
2. `window.__MEDWATCH_BACKEND_PORT__` injection is implemented on the consumer side only; the Wave 5 Electron preload still needs to actually call `contextBridge.exposeInMainWorld("__MEDWATCH_BACKEND_PORT__", port)` (or write a `<script>` tag into the HTML head before load).
3. Client-side role gate to replace the deleted `src/proxy.ts`. Today, the backend enforces role at the API layer (already verified by Wave 0 scout). A defense-in-depth UI-side guard inside `AppShell` is a follow-up; Wave 3 does not block on it.
4. The route `/patients/edit/?id=<id>` is functionally equivalent to the previous `/patients/<id>/` from a user perspective, but external deep links from prior sessions (bookmarks, share URLs) pointing at `/patients/<id>/` will 404 on the desktop bundle. UNVERIFIED whether any existing teammate workflow depended on the dynamic shape; the patient roster and the create-new flow have both been updated to emit the new URL shape.

End of Wave 3 frontend-bundler findings.
