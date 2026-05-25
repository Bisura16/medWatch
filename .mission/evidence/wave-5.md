# Wave 5 evidence: binaries produced

Captured 2026-05-25 by integration-builder subagent (re-dispatch starting at Phase 2 after manager-run Docker pull).

## medwatch-backend.exe (PLACEHOLDER)

- Path: `dist-windows/medwatch-backend.exe`
- Size: 262944 bytes (257 KiB)
- SHA256: `77c6281250abc2faa0fe51dbee12620b4c60e639e073198ac1bb5722fba67371`
- Type: `PE32+ executable (console) x86-64, for MS Windows`
- Provenance: cross-compiled from a minimal C stub with `dockcross/windows-static-x64:latest` (MinGW-w64 GCC 11.4.0, static link). NOT a real PyInstaller bundle of the Flask backend.
- Reason for placeholder: Wine inside the `electronuserland/builder:wine` Docker image crashes with `anon_mmap_fixed` assertion under QEMU userland emulation on macOS arm64 host. Both the standard and `wine-mono` variants exhibit the same crash. PyInstaller cannot build a Windows binary without Wine. See `KNOWN_LIMITATION_BACKEND_EXE.md` and `.mission/findings/wave-5-build.md`.
- Runtime behavior on Windows: prints a Bahasa-aware diagnostic to stderr, opens a MessageBox titled "MedWatch backend (placeholder)", returns exit code 1. Electron main process will report "Backend MedWatch gagal dimulai." dialog and exit per the spec.

This same placeholder is copied verbatim into both variants' `resources/medwatch-backend.exe`. Each copy has the same SHA256 above.

## installer-based variant: MedWatch Setup 0.1.0.exe (NSIS x64)

- Path: `installer-based app/dist/MedWatch Setup 0.1.0.exe`
- Size: 145592112 bytes (139 MiB)
- SHA256: `ec7c3c8744f35618b30271d28d7ff2b9a20a66a4e0f8168a1ee3cec367637470`
- Type: `PE32 executable (GUI) Intel 80386, for MS Windows, Nullsoft Installer self-extracting archive`
- Sub-type: NSIS-3 Unicode, x64 payload
- BlockMap: `installer-based app/dist/MedWatch Setup 0.1.0.exe.blockmap` (149 KiB)

Build provenance:
- electron-builder 26.11.1 on macOS host (darwin 25.3.0)
- electron 36.9.5
- target: nsis, arch: x64
- payload includes: app.asar (2.1 MB), drugs.db (237 MB), medwatch-backend.exe placeholder (257 KB), elevate.exe (105 KB), full Electron runtime
- NSIS uninstaller generated via electron-builder's pure-JS `UninstallerReader.exec` path because `isMacOsCatalina` returns true on a macOS host newer than 10.15. This avoids the wine call that fails inside Docker on Apple Silicon.

## portable variant: MedWatch-0.1.0-portable.exe

- Path: `portable-app/dist/MedWatch-0.1.0-portable.exe`
- Size: 117895251 bytes (112 MiB)
- SHA256: `c2ccd91abb5315b48c0af56bd25b415d19b43bf71876b151268389bbe68cd0ab`
- Type: `PE32 executable (GUI) Intel 80386, for MS Windows, Nullsoft Installer self-extracting archive`
- Sub-type: NSIS-3 Unicode SFX wrapping a 7z archive (`$PLUGINSDIR/app-64.7z`, 117 MB compressed)

Build provenance:
- electron-builder 26.11.1 inside `electronuserland/builder:wine` Docker container (linux/amd64, QEMU userland on macOS arm64 host)
- electron 36.9.5
- target: portable, arch: x64
- Portable target succeeds inside Docker because it does NOT generate a separate uninstaller (the portable .exe just self-extracts to %TEMP% and launches MedWatch.exe).

## Source-of-truth resources packaged in both installers

Both installers contain identical resources under `resources/`:

- `drugs.db`: 237 MiB, sha256 `76be06d65ada4ac13dc17786a76214d36fc496ba08d3222aff1b4660f86b0bae`
- `medwatch-backend.exe`: 257 KiB placeholder, sha256 `77c6281250abc2faa0fe51dbee12620b4c60e639e073198ac1bb5722fba67371`
- `renderer/` directory: Next.js static export from Wave 3
- `app.asar`: 2.1 MiB containing main/, preload/, package.json

The drugs.db SHA256 matches the source `installer-based app/resources/drugs.db` and `portable-app/resources/drugs.db` (Wave 4 deliverables, identical files).

## Wall-clock per phase

- Phase 2 (backend.exe): 2 minutes (1 minute Wine crash detection, 1 minute MinGW cross-compile placeholder)
- Phase 3 (copy resources): under 1 second
- Phase 4 (electron-builder.yml audit): no edits needed (manager had already wired both files correctly)
- Phase 5 (NSIS Docker attempt 1): 2 minutes wall, failed at uninstaller-readback wine call
- Phase 5 (NSIS Docker attempt 2 with `--publish=never`): 4 minutes wall, same failure
- Phase 5 (NSIS macOS host retry, x64): 1 minute 7 seconds, SUCCESS
- Phase 6 (portable Docker, x64): 3 minutes 24 seconds, SUCCESS first try
- Phase 7 + 8 (metadata, evidence, findings): in progress

Total wall clock from start: approximately 24 minutes.
