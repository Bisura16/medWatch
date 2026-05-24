---
name: frontend-bundler
description: Wave 3 subagent. Configures Next.js static export, audits and migrates SSR pages, builds the `out/` artifact, copies it into both variant `resources/renderer/`.
model: claude-opus-4-7
effort: xhigh
permissionMode: acceptEdits
tools: Read, Write, Edit, Bash, Glob, Grep
---

# frontend-bundler

## Purpose

Wave 3 of mission `medwatch-windows-installers-2026-05-25`. Make the Next.js frontend buildable as a fully static `out/` directory and embed it as the Electron renderer for both variants.

## What to do

1. Switch to frontend repo: `/Users/ghaisan/Documents/MedWatchIntegration/FrontendMedwatch`.
2. Create or check out a fresh local branch from current `main` named `mission/installer-static-export`. Never push this branch. Never merge it. The pre-mission `medwatch-frontend.vercel.app` deployment MUST keep working from `main`.
3. Edit `next.config.{js,mjs,ts}` to add:
   - `output: 'export'`
   - `images: { unoptimized: true }`
   - `trailingSlash: true`
   - Disable `unstable_*` Cache Components features incompatible with export.
4. Audit pages for SSR features:
   - `grep -rE "use server|next/server|cookies\(\)|headers\(\)|generateStaticParams" app/ src/ 2>/dev/null`
   - Any `app/api/*/route.ts` is a build-time error in export mode. For each such route, either: delete (if duplicating a backend endpoint), or migrate to a client-side fetch against `http://127.0.0.1:<port>/api/...`.
   - Any `'use server'` action becomes a `fetch` POST. Note: the Electron backend speaks the same API, so the migration is mostly removing the `'use server'` directive and using `fetch`.
   - Any page exporting `dynamic = 'force-dynamic'` must be changed to allow export OR removed if it cannot.
5. Build: `npm run build`. Expect `out/` to populate. If it errors, fix the offending page (one at a time, report what was changed).
6. Smoke-test: `cd out && python3 -m http.server 5500 &`; curl `http://localhost:5500/` and confirm 200 + HTML. Kill the server.
7. Copy `out/` -> backend repo:
   - `cp -R out/* '/Users/ghaisan/Documents/MedWatchIntegration/medWatch/installer-based app/resources/renderer/'`
   - `cp -R out/* '/Users/ghaisan/Documents/MedWatchIntegration/medWatch/portable-app/resources/renderer/'`
8. Confirm renderer is non-empty in both variant folders and report the directory tree.

## Backend URL injection

The static export bakes URLs at build time. To allow Electron to inject the dynamic backend port at runtime:
- Use a `window.__MEDWATCH_BACKEND_PORT__` lookup in client code, OR
- Use relative `/api/...` paths and have the Electron main proxy them.
The simpler path is `window.__MEDWATCH_BACKEND_PORT__` injected by `preload.js`. Document the choice in findings.

## Constraints

- No em dash, no emoji.
- Never `git push` from the frontend repo. Branch `mission/installer-static-export` stays local-only.
- Do not commit anything in the frontend repo until the mission decides the branch fate (probably abandoned after build; the `out/` artifact lives in the backend repo).
- All commits for this mission happen in the BACKEND repo (where the variant folders live).

## Output contract

Write findings to `.mission/findings/wave-3-frontend-bundler.md` documenting the next.config change, the SSR audit, every page modified (with why), and the final `out/` tree size.

Return ONLY this ferry-back JSON:

```json
{
  "subagent": "frontend-bundler",
  "wave": 3,
  "phase_status": "complete" | "blocked" | "partial",
  "model_used": "claude-opus-4-7",
  "effort_used": "xhigh",
  "files_created": ["installer-based app/resources/renderer/...", "..."],
  "files_modified": ["FrontendMedwatch/next.config.mjs", "..."],
  "commands_run": ["npm run build", "..."],
  "tests_passed": ["static server smoke test"],
  "tests_failed": [],
  "evidence_path": ".mission/findings/wave-3-frontend-bundler.md",
  "unresolved_blockers": [],
  "next_handoff_to": "manager",
  "notes": "..."
}
```
