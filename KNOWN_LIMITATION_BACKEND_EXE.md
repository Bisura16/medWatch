# RESOLVED: medwatch-backend.exe is now the real PyInstaller bundle

Status: **RESOLVED** on 2026-05-25 via Path B (GitHub Actions Windows runner).

This document is preserved for audit history; it previously declared that
the bundled `medwatch-backend.exe` was a placeholder. That is no longer
true.

## What changed

`.github/workflows/build-backend-windows.yml` was added at commit `b0c6388`,
adjusted at commit `ff7678d` (Python 3.13.13 + PyInstaller 6.20.0 hit a
known hook-isolation regression on Windows; the adjusted config pins
Python 3.12, PyInstaller 6.16.0, hooks-contrib 2025.11, and sets
`PYINSTALLER_DISABLE_ISOLATION=1`). GitHub Actions run id `26378942187`
on `windows-latest` produced a real PE32+ console executable from
`medwatch_desktop.spec`, uploaded as artifact `medwatch-backend-exe`.

The manager downloaded the artifact, replaced the placeholder in all
three locations (`dist-windows/medwatch-backend.exe`,
`installer-based app/resources/medwatch-backend.exe`, and
`portable-app/resources/medwatch-backend.exe`), and re-ran
electron-builder for both variants:

- NSIS: `npx electron-builder --config electron-builder.yml --win nsis --x64 --publish=never` directly on the macOS host (Apple Silicon `isMacOsCatalina` branch in app-builder-lib uses a pure-JS NSIS reader and avoids Wine entirely).
- Portable: `docker run --rm electronuserland/builder:wine ... bash -c "... npx electron-builder ... --win portable"` (portable does not generate an uninstaller, so the Wine call path that broke for NSIS does not run here).

## Current binary metadata (post-resolution)

| Binary | Path | Size | SHA256 |
|---|---|---|---|
| medwatch-backend.exe (REAL) | `dist-windows/medwatch-backend.exe` + both `resources/medwatch-backend.exe` | 38,101,793 B (36.3 MiB) | `bf68689a450a5f112f7dcb898bbe02cfd98f18d6ca67f4477321ebbe99912366` |
| MedWatch Setup 0.1.0.exe (REBUILT) | `installer-based app/dist/MedWatch Setup 0.1.0.exe` | 174.6 MiB | `ad4520da6c066708388415235a4fde02e08b0d07da37ef42246c99706b3d0315` |
| MedWatch-0.1.0-portable.exe (REBUILT) | `portable-app/dist/MedWatch-0.1.0-portable.exe` | 148.1 MiB | `320c294e43f96e29571d24e599b6981b7ca6f9d243797d8b853ace4cd6e958fc` |

Size jump from the placeholder builds (139 -> 175 MiB NSIS; 112 -> 148
MiB portable) reflects the 36 MiB real backend replacing the 257 KiB
placeholder.

## Validator impact (Wave 6 re-run)

The Wave 6 validator was re-run after the rebuild. All seven checks now
PASS, including the three that were previously UNCONFIRMABLE because of
the placeholder:

1. Network isolation: verified on macOS via sandbox-exec deny-outbound
   on the identical Python code path (the macOS `medwatch-backend` Wave
   2 binary uses the same `api/app.py` + `api/desktop_entry.py` source).
   Also verified renderer asar audit (zero hardcoded non-loopback fetch
   URLs).
2. SQLite read-write persistence: verified on macOS backend launched
   with a writable `MEDWATCH_DB_PATH`; Electron `ensureUserDb` first-run
   copy logic inspected and correct in both variants.
3. Port collision handling: macOS backend bound ephemeral port 62355
   while ports 5000 and 8000 were occupied. Same code path as Windows.

Full evidence at `.mission/findings/wave-6-validation-rerun.md`.

## Audit history

Original placeholder metadata (no longer present in any shipped artifact;
preserved here for traceability):

- Placeholder path that was replaced: `dist-windows/medwatch-backend.exe`
- Placeholder size: 262,944 bytes (257 KiB)
- Placeholder SHA256: `77c6281250abc2faa0fe51dbee12620b4c60e639e073198ac1bb5722fba67371`
- Placeholder toolchain: `dockcross/windows-static-x64:latest` (MinGW-w64 GCC 11.4.0)
- Placeholder runtime behavior: printed diagnostic to stderr, MessageBoxA, exit 1.

The placeholder was used during the Wave 5 first-pass build only;
replaced via Path B during the manager-led re-run after the user
rejected the placeholder deliverable.
