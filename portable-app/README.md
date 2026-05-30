# MedWatch Desktop (Portable Variant)

## What this is

This is the single-file portable variant of MedWatch Desktop, the Windows desktop wrapper for the MedWatch project. MedWatch provides a clinical drug-safety reference (openFDA prescription label data, adverse-reaction frequencies, drug recalls) plus patient SOAP CRUD for Faskes 1 bidan workflow. The portable executable is a self-extracting bundle that ships the entire openFDA prescription dataset locally as a SQLite file, so the application is fully offline at runtime. No installation step is required: the user double-clicks the .exe to launch. It is intended for Windows 10 and Windows 11 on x86_64.

## Output

Binary path: `portable-app/dist/MedWatch-0.1.0-portable.exe`.

Size: 112 MiB (117,895,251 bytes).

SHA256: `c2ccd91abb5315b48c0af56bd25b415d19b43bf71876b151268389bbe68cd0ab`.

The `medwatch-backend.exe` embedded inside this bundle is a placeholder pending replacement via the procedure described in the "Known limitation" section below.

## Build from source on macOS host

```
docker pull electronuserland/builder:wine
cd 'portable-app'
docker run --rm --platform linux/amd64 -v "$PWD:/project" -w /project \
  electronuserland/builder:wine bash -c "\
    npm install --no-audit --no-fund && \
    npx electron-builder --config electron-builder.yml --win portable --publish=never"
```

The portable target does NOT generate a separate uninstaller (the portable .exe self-extracts to `%TEMP%` and launches MedWatch.exe directly; there is no install state to uninstall). Without uninstaller generation, electron-builder never calls `execWine`, so the QEMU plus Wine crash path that blocks the NSIS Docker build is bypassed. The portable build therefore completes inside the official `electronuserland/builder:wine` container on macOS arm64.

Wall-clock build time on a 2024 M-series MacBook is about 3 minutes 24 seconds (40 seconds npm install, the rest electron plus 7z packaging).

## Build from source on Windows host

Follow Path B (GitHub Actions Windows runner) described in the team build runbook. The workflow checks out the repo on `windows-latest`, runs PyInstaller against `medwatch_desktop.spec` to produce the real `medwatch-backend.exe`, copies the result into both variant `resources/` folders, then runs `npx electron-builder --config electron-builder.yml --win portable` from this folder.

## What this contains

The bundle ships these payloads under `resources/`:

- Static Next.js export (the renderer tree, about 2.5 MiB).
- PyInstaller-bundled Flask backend as `medwatch-backend.exe` (PLACEHOLDER, see below).
- SQLite drug database `drugs.db` (246 MiB, SHA256 `76be06d65ada4ac13dc17786a76214d36fc496ba08d3222aff1b4660f86b0bae`).

The Electron 36 main process spawns the backend as a child process, waits for the port handshake on stdout, then loads the Next.js export into a `BrowserWindow`.

## Known limitation (backend.exe)

The `medwatch-backend.exe` inside this portable bundle is currently a 257 KiB placeholder, not a real PyInstaller bundle. The placeholder displays an error dialog and exits with code 1, so the application UI will show "Backend MedWatch gagal dimulai" on launch. The build host (macOS arm64) cannot run PyInstaller against a Windows Python interpreter because Wine in Docker crashes on Apple Silicon. The replacement procedure (Path A native Windows, Path B GitHub Actions Windows runner) is described in the "Build from source on Windows host" section above.

## SmartScreen first-run warning

Windows SmartScreen warns on first run because the .exe is unsigned. Click `More info` then `Run anyway`. Code signing is out of scope for this academic submission.

## Offline operation

All drug data ships in `drugs.db`. The app does NOT require internet at runtime. Network isolation is verified by the user on a Windows VM as part of release validation.

## Portable launch behavior

Double-clicking the .exe extracts the bundle contents to `%LOCALAPPDATA%\Temp` on first launch (subdirectory named after a content hash), then spawns `MedWatch.exe` from that temp directory. Subsequent launches reuse the same extracted copy if the hash matches, so cold-start cost is paid only once per executable version. Deleting the portable .exe does not remove the extracted temp copy; Windows will clean it up on the next disk-cleanup cycle.

## Database location

First launch copies the bundled `drugs.db` from the extracted `resources/` to `%APPDATA%\MedWatch\drugs.db`. User edits land in the writable copy at that location. This means patient SOAP records and any database mutations PERSIST across portable runs even though the application itself is "portable" in the sense of no installer.

## Maintainer

Ghaisan Khoirul Badruzaman <ghaisan.khoirul.b@gmail.com> (Project Leader, Kelompok B5, POLBAN D4 Teknik Informatika 1B-D4, AT 2025/2026).
