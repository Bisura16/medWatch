# MedWatch Desktop (Installer Variant)

## What this is

This is the NSIS installer wizard variant of MedWatch Desktop, the Windows desktop wrapper for the MedWatch project. MedWatch provides a clinical drug-safety reference (openFDA prescription label data, adverse-reaction frequencies, drug recalls) plus patient SOAP CRUD for Faskes 1 bidan workflow. The packaged installer bundles the entire openFDA prescription dataset locally as a SQLite file, so the application is fully offline at runtime. It is intended for Windows 10 and Windows 11 on x86_64.

## Output

Binary path: `installer-based app/dist/MedWatch Setup 0.1.0.exe`.

Size: 139 MiB (145,592,112 bytes).

SHA256: `ec7c3c8744f35618b30271d28d7ff2b9a20a66a4e0f8168a1ee3cec367637470`.

The `medwatch-backend.exe` embedded inside this bundle is a placeholder pending replacement via the procedure described in the "Known limitation" section below.

## Build from source on macOS host

```
docker pull electronuserland/builder:wine
cd 'installer-based app'
npx electron-builder --config electron-builder.yml --win nsis --x64 --publish=never
```

The second command runs directly on the macOS host, not inside Docker. On darwin newer than Catalina, electron-builder's `NsisTarget.buildInstaller` takes the pure-JS `UninstallerReader.exec` branch (it parses the NSIS PE file in Node and extracts the embedded uninstaller bytes) instead of invoking Wine. The Docker pull is kept for parity with the portable variant build, but it is not strictly required for the NSIS target on macOS.

Wine in Docker does not work on macOS arm64 because of a Wine plus QEMU plus 16 KiB host-page-size assertion crash. The host-side build via `npx electron-builder` is the practical Apple-Silicon path.

## Build from source on Windows host

Follow Path B (GitHub Actions Windows runner) in `.mission/findings/wave-2-runbook-windows-build.md`. The workflow checks out the repo on `windows-latest`, runs PyInstaller against `medwatch_desktop.spec` to produce the real `medwatch-backend.exe`, copies the result into both variant `resources/` folders, then runs `npx electron-builder --config electron-builder.yml --win nsis` from this folder.

## What this contains

The bundle ships these payloads under `resources/`:

- Static Next.js export from Wave 3 (the renderer tree, about 2.5 MiB).
- PyInstaller-bundled Flask backend as `medwatch-backend.exe` (PLACEHOLDER, see below).
- SQLite drug database `drugs.db` (246 MiB, SHA256 `76be06d65ada4ac13dc17786a76214d36fc496ba08d3222aff1b4660f86b0bae`).

The Electron 36 main process spawns the backend as a child process, waits for the port handshake on stdout, then loads the Next.js export into a `BrowserWindow`.

## Known limitation (backend.exe)

The `medwatch-backend.exe` inside this installer is currently a 257 KiB placeholder, not a real PyInstaller bundle. The placeholder displays an error dialog and exits with code 1, so the application UI will show "Backend MedWatch gagal dimulai" on launch. The build host (macOS arm64) cannot run PyInstaller against a Windows Python interpreter because Wine in Docker crashes on Apple Silicon. The replacement procedure (Path A native Windows, Path B GitHub Actions Windows runner) is documented in `KNOWN_LIMITATION_BACKEND_EXE.md` at the repo root.

## SmartScreen first-run warning

Windows SmartScreen warns on first run because the .exe is unsigned. Click `More info` then `Run anyway`. Code signing is out of scope for this academic submission.

## Offline operation

All drug data ships in `drugs.db`. The app does NOT require internet at runtime. Network isolation will be verified by the user on a Windows VM per `.mission/findings/wave-6-validation.md`.

## Database location

First launch copies the bundled `drugs.db` from `resources/` to `%APPDATA%\MedWatch\drugs.db` on Windows. User edits land in the writable copy at that location. The bundled copy under `resources/` remains read-only.

## Maintainer

Ghaisan Khoirul Badruzaman <ghaisan.khoirul.b@gmail.com> (Project Leader, Kelompok B5, POLBAN D4 Teknik Informatika 1B-D4, AT 2025/2026).
