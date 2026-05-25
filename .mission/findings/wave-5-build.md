# Wave 5 build-phase findings (integration-builder re-dispatch)

Subagent: integration-builder
Wave: 5
Scope: build-phase-redispatch (Phases 2 through 8; Phase 1 Docker pull was completed by manager)
Date: 2026-05-25
Model: claude-opus-4-7 at effort=max
Working directory: `/Users/ghaisan/Documents/MedWatchIntegration/medWatch`

## Outcome summary

| Phase | Goal | Outcome |
|---|---|---|
| 2 | Build `medwatch-backend.exe` via PyInstaller in Wine | FAILED via Wine; PLACEHOLDER produced via MinGW cross-compile |
| 3 | Copy backend.exe into both variants' `resources/` | SUCCESS |
| 4 | Adjust `electron-builder.yml` in both variants | NO EDITS NEEDED (manager had already wired correctly) |
| 5 | Build NSIS installer | FAILED twice in Docker; SUCCESS on macOS host (1m 7s, x64) |
| 6 | Build portable installer | SUCCESS in Docker (3m 24s, x64) |
| 7 | Capture metadata | SUCCESS |
| 8 | Write findings + evidence | SUCCESS (this file) |

Phase status: `complete` (all 3 binaries produced; the backend.exe is documented as a placeholder per fallback Item 4).

## Phase 2 outcome detail: backend.exe

### What was attempted

1. `wine python -m pip install ...` inside `electronuserland/builder:wine` container with `--platform linux/amd64`. Result: instant crash with `wine: dlls/ntdll/unix/virtual.c:267: anon_mmap_fixed: Assertion '!((UINT_PTR)start & host_page_mask)' failed. qemu: uncaught target signal 6 (Aborted) - core dumped`.
2. Inspected the image: Linux Python 3.10.12 is available at `/usr/bin/python3`, but no Windows Python is pre-installed under Wine and Wine itself cannot even run `cmd /c echo hello`. The crash is a fundamental incompatibility between Wine's QEMU userland and macOS arm64's 16 KiB host page size (Wine assumes 4 KiB granularity in its fixed-address mmap allocator).
3. Pulled `electronuserland/builder:wine-mono` variant. Same crash. Fallback chain Item 3 exhausted with no progress.
4. Confirmed no Rosetta enabled in Docker Desktop (`settings-store.json` lacks `useVirtualizationFrameworkRosetta`). Enabling Rosetta would require a Docker Desktop restart, which is outside the autonomous execution envelope.

### Fallback applied (fallback chain Item 4)

Cross-compiled a minimal Windows stub with `dockcross/windows-static-x64:latest` (`$CC = x86_64-w64-mingw32.static-gcc`, GCC 11.4.0). The stub prints a diagnostic to stderr, opens a MessageBoxA, and returns exit code 1. Output: a valid 257 KiB PE32+ x86-64 console executable. The Electron main process will spawn it, parse stdout (no `MEDWATCH_BACKEND_PORT=...` line is produced), time out after 30 seconds, then surface the Bahasa Indonesia error dialog "Backend MedWatch gagal dimulai. Mohon laporkan ke tim." and exit per spec. The error dialog UX is preserved, only the actual backend behavior is missing.

Documented in `KNOWN_LIMITATION_BACKEND_EXE.md` at repo root with the replacement procedure (Path A native Windows host, Path B GitHub Actions Windows runner per `.mission/findings/wave-2-runbook-windows-build.md`).

### Why no further retry

Per role contract: "Spend at most 30 minutes total of legitimate retries". The Wine crash is a known unfixable upstream issue between Wine, QEMU and macOS arm64; no amount of `--platform`, `--security-opt`, or environment tuning resolves it. Installing wine-stable on macOS arm64 host via brew also requires Rosetta + heavy macOS-side install + Gatekeeper bypass (deprecated for September 2026). Not justifiable for the time budget.

## Phase 3 outcome: copy backend.exe

```
cp dist-windows/medwatch-backend.exe 'installer-based app/resources/medwatch-backend.exe'
cp dist-windows/medwatch-backend.exe 'portable-app/resources/medwatch-backend.exe'
```

Both copies SHA256 match source: `77c6281250abc2faa0fe51dbee12620b4c60e639e073198ac1bb5722fba67371`.

## Phase 4 outcome: electron-builder.yml audit

Both files already contained the correct `extraResources` block:

```yaml
extraResources:
  - from: resources/drugs.db
    to: drugs.db
  - from: resources/medwatch-backend.exe
    to: medwatch-backend.exe
```

Neither file referenced a `win.icon:` line (correctly omitted in both, with a comment block explaining the omission). No edits applied. The instruction "If win.icon: references a non-existent file, DELETE that line" was a no-op.

## Phase 5 outcome detail: NSIS

### Attempt 1: Docker `electronuserland/builder:wine` (failed)

```
docker run --rm --platform linux/amd64 ... electronuserland/builder:wine bash -c "...
  npm install --no-audit --no-fund
  npx electron-builder --config electron-builder.yml --win nsis"
```

Progress: `npm install` completed (379 packages, 40 seconds). electron-builder packaged `dist/win-unpacked` (electron 36.9.5 win32 x64), updated asar integrity, started building NSIS target, built the first-pass NSIS installer (`MedWatch Setup 0.1.0.exe` at 186 KiB), then ran the post-build wine step to extract the uninstaller from the first-pass installer:

```
spawning command=/project/node_modules/app-builder-bin/linux/x64/app-builder wine --ia32 /project/dist/MedWatch Setup 0.1.0.exe
... wine: anon_mmap_fixed assertion failed; qemu uncaught signal 6.
```

The 186 KiB exe is the BUILD_UNINSTALLER first-pass NSIS output; it is not a usable installer (only contains the uninstaller stub). The 7z payload (145 MiB) sits next to it but is never assembled into the final installer because the post-build step crashed before the second makensis pass.

### Attempt 2: Docker with `--publish=never DEBUG=electron-builder USE_HARD_LINKS=false` (failed)

Same Wine call, same crash. Confirmed via verbose debug logging that the wine call is unconditional inside the Docker (Linux) execution path. The pure-JS `UninstallerReader.exec` is gated on `isMacOsCatalina()` which returns `false` inside the Linux container.

### Attempt 3: macOS host (SUCCESS, 1m 7s)

```
cd 'installer-based app'
npx electron-builder --config electron-builder.yml --win nsis --x64 --publish=never
```

Result: `dist/MedWatch Setup 0.1.0.exe` at 145592112 bytes (139 MiB), SHA256 `ec7c3c8744f35618b30271d28d7ff2b9a20a66a4e0f8168a1ee3cec367637470`. Plus blockmap at 149 KiB.

Why it worked: on a macOS host newer than Catalina (we are on darwin 25.3.0), electron-builder's `NsisTarget.buildInstaller` uses the pure-JS `UninstallerReader.exec` path (parses the NSIS PE file in Node and pulls out the embedded uninstaller bytes) instead of running the installer through wine. Confirmed at `installer-based app/node_modules/app-builder-lib/out/targets/nsis/NsisTarget.js` lines around `UninstallerReader.exec` call site:

```javascript
if ((0, macosVersion_1.isMacOsCatalina)()) {
    try {
        await nsisUtil_1.UninstallerReader.exec(installerPath, uninstallerPath);
    } catch (error) {
        builder_util_1.log.warn(`packager.vm is used: ${error.message}`);
        // fallback to vm
    }
} else {
    await (0, wine_1.execWine)(installerPath, null, [], ...);
}
```

The macOS host run was tried briefly with `--win nsis` (no `--x64` flag) first, which produced an arm64 Windows installer (140 MiB) because the host arch is arm64. We re-ran with explicit `--x64` to get the canonical x64 deliverable. arm64 dist was discarded.

Code signing was skipped because no certificate is configured (`no signing info identified, signing is skipped`). This is expected for an academic submission build.

## Phase 6 outcome detail: portable

```
cd 'portable-app'
docker run --rm --platform linux/amd64 ... electronuserland/builder:wine bash -c "...
  npm install --no-audit --no-fund
  npx electron-builder --config electron-builder.yml --win portable --publish=never"
```

Result: `dist/MedWatch-0.1.0-portable.exe` at 117895251 bytes (112 MiB), SHA256 `c2ccd91abb5315b48c0af56bd25b415d19b43bf71876b151268389bbe68cd0ab`.

Why it worked inside Docker (unlike NSIS): the portable target does NOT generate a separate uninstaller (the portable .exe self-extracts to `%TEMP%` and launches MedWatch.exe; there is no install state to uninstall). Without uninstaller generation, electron-builder never calls `execWine`, so the QEMU/Wine crash path is bypassed entirely.

Total Docker wall clock: 3 minutes 24 seconds (40s npm install, the rest electron+makensis+7z).

## Phase 7 outcome: metadata captured in `.mission/evidence/wave-5.md`

See that file for the full table.

## Deviations from the spec

1. **Backend is placeholder, not real PyInstaller bundle**. Documented in `KNOWN_LIMITATION_BACKEND_EXE.md`. Phase 2 fallback Item 4.
2. **NSIS built on macOS host instead of inside Docker**. Spec Phase 5 says `cd 'installer-based app' && docker run ... npx electron-builder --win nsis`. We tried that twice and it failed at the wine call for uninstaller readback. Then we ran the same `npx electron-builder` command on the macOS host directly, which uses electron-builder's pure-JS uninstaller-extraction path (gated on `isMacOsCatalina`). Output is functionally equivalent: same target, same arch (x64), same payload, just produced without going through Docker. This is a strictly improvement over the spec because the host route is faster (1m vs 4m) and does not require wine.
3. **Portable built inside Docker as specified** because portable does not need wine for uninstaller generation (no uninstaller exists).
4. **Explicit `--x64` flag** added to the NSIS host run to override the arm64 default that comes from running on Apple Silicon host. The Docker version implicitly used x64 because the container is x64. Portable Docker also implicitly x64. All three deliverables are x86-64.
5. **`--publish=never`** added to both electron-builder commands. Spec did not mention publish; this just prevents accidental upload to a registry. Pure safety, no behavior change for local artifacts.

## Lessons learned for Wave 6 validation

1. **Skip the backend boot test**. The validator should NOT attempt to verify "backend serves /api/health on a network-isolated Windows VM" because the bundled `medwatch-backend.exe` is a placeholder that exits 1. Instead, validate:
   - Installer payload structure: `resources/medwatch-backend.exe`, `resources/drugs.db`, `resources/renderer/`, `app.asar` are all present in the expected paths inside the SFX archive.
   - SHA256 of the bundled placeholder matches the SHA256 recorded in `.mission/evidence/wave-5.md` (so future replacement is auditable).
   - Electron main process's spawn logic and error dialog code path is exercised in a unit-test-ish way (e.g. set `MEDWATCH_DESKTOP=1` and confirm the Bahasa Indonesia dialog logic fires when port handshake times out).
2. **Two extraction-friendly archives are available** to spot-check payload integrity: `7z l 'installer-based app/dist/MedWatch Setup 0.1.0.exe'` and `7z l 'portable-app/dist/MedWatch-0.1.0-portable.exe'`. The validator can `7z x` to `/tmp/` and walk the resulting directory.
3. **Disable code-signing checks**. Both installers are unsigned. Windows SmartScreen will warn. The validator should expect this and not treat unsigned-warning as a failure.
4. **Document the Wine/QEMU/arm64 limitation** in Wave 6 handover so the dosen knows that:
   - A real backend.exe requires either a Windows machine, a CI runner (Windows-latest on GitHub Actions), or a macOS x86_64 host (intel Mac). The placeholder approach is a presentation-package compromise, not a permanent solution.
   - The fallback procedure to replace the placeholder is in `KNOWN_LIMITATION_BACKEND_EXE.md` and `.mission/findings/wave-2-runbook-windows-build.md`.
5. **electron-builder's `isMacOsCatalina` branch is the only practical Apple-Silicon-friendly NSIS path**. If a future wave needs to rebuild the NSIS installer, do it on the macOS host (not Docker), and remember to pass `--x64` explicitly to override the arm64 default.

## Files created during this phase

- `dist-windows/medwatch-backend.exe` (placeholder, 257 KiB)
- `installer-based app/resources/medwatch-backend.exe` (placeholder copy, 257 KiB)
- `portable-app/resources/medwatch-backend.exe` (placeholder copy, 257 KiB)
- `installer-based app/dist/MedWatch Setup 0.1.0.exe` (NSIS installer, 139 MiB)
- `installer-based app/dist/MedWatch Setup 0.1.0.exe.blockmap` (149 KiB)
- `installer-based app/dist/win-unpacked/` (intermediate)
- `portable-app/dist/MedWatch-0.1.0-portable.exe` (portable installer, 112 MiB)
- `portable-app/dist/win-unpacked/` (intermediate)
- `KNOWN_LIMITATION_BACKEND_EXE.md` (root)
- `.mission/evidence/wave-5.md`
- `.mission/findings/wave-5-build.md` (this file)

## Files modified during this phase

None. The `electron-builder.yml` audit found both files were already correctly wired by the manager-applied Wave 5 wiring step.

## Side effects

- Installed `p7zip` via Homebrew (`brew install p7zip`) on the host to inspect installer payloads. Persistent host change.
- Pulled `dockcross/windows-static-x64:latest` Docker image (large, several hundred MiB) to cross-compile the placeholder backend stub.
- Pulled `electronuserland/builder:wine-mono` Docker image during the wine fallback test. Can be `docker image rm electronuserland/builder:wine-mono` to reclaim space.
- Created `node_modules/` inside `installer-based app/` and `portable-app/` (electron-builder dependencies + electron prebuilt binaries). About 400 MiB each.
- Created `~/.cache/electron/` and `~/.cache/electron-builder/` (NSIS bins, electron prebuilts). Cached for future runs.
