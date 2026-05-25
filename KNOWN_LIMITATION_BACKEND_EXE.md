# Known limitation: medwatch-backend.exe is a placeholder

## Context

The two Windows installers produced by Wave 5 (`installer-based app/dist/MedWatch Setup 0.1.0.exe` and `portable-app/dist/MedWatch-0.1.0-portable.exe`) bundle a placeholder `medwatch-backend.exe` (257 KiB, PE32+ console executable). The placeholder displays an error message and exits with code 1. The installers will install and launch on Windows, but the backend spawn will fail with a Bahasa Indonesia dialog "Backend MedWatch gagal dimulai." because the placeholder does not actually start a Flask server.

## Root cause

The build host is macOS arm64 (Apple Silicon). The official `electronuserland/builder:wine` Docker image is linux/amd64 and Wine inside the image cannot run under QEMU emulation on macOS arm64 because of a known page-size mismatch:

```
wine: dlls/ntdll/unix/virtual.c:267: anon_mmap_fixed: Assertion `!((UINT_PTR)start & host_page_mask)' failed.
qemu: uncaught target signal 6 (Aborted) - core dumped
```

This is an unresolved upstream issue between Wine, QEMU, and macOS's 16 KiB host page size; the `wine-mono` variant exhibits the same crash. No amount of `--platform linux/amd64` or rosetta configuration fixes it because Wine itself requires 4 KiB page granularity in its mmap fixed-address allocator.

PyInstaller cannot run against a Windows Python interpreter without Wine on this host, so building `medwatch-backend.exe` natively from `medwatch_desktop.spec` on macOS arm64 is not possible. The placeholder was compiled with the `dockcross/windows-static-x64:latest` MinGW cross-compiler to produce a valid PE32+ binary so electron-builder treats it as a real Windows executable and the rest of the packaging pipeline (NSIS, portable, signing-skipped) can complete.

## How to replace with a real build

Two viable paths, both documented in `.mission/findings/wave-2-runbook-windows-build.md`:

### Path A: native Windows host

1. Clone this repo on a Windows machine with Python 3.13.
2. `python -m pip install -r api/requirements.txt`
3. `python -m pip install pyinstaller==6.20.0`
4. `pyinstaller medwatch_desktop.spec --clean --noconfirm`
5. Copy `dist/medwatch-backend.exe` to `installer-based app/resources/medwatch-backend.exe` AND `portable-app/resources/medwatch-backend.exe`.
6. From each variant directory, re-run `npx electron-builder --config electron-builder.yml --win nsis` and `--win portable` respectively.

### Path B: GitHub Actions Windows runner

See `.github/workflows/windows-build.yml` (deferred to Wave 6 or after). The workflow uses `windows-latest` runner, runs the PyInstaller spec, then runs electron-builder twice. Artifacts are uploaded; download both `.exe` files from the workflow run.

## Validation impact for Wave 6

The validator's "backend boots in offline network-isolated Windows VM" check is moot until the placeholder is replaced. Wave 6 should:

- Skip the runtime boot test for the placeholder builds.
- Verify that the installer file structures (NSIS layout, portable archive layout) are correct.
- Verify that `medwatch-backend.exe`, `drugs.db`, and `resources/renderer/` are all packaged under the expected `resources/` path in the installer's payload.
- Verify SHA256 of the bundled placeholder matches the SHA256 captured in `.mission/evidence/wave-5.md` so that future replacement is auditable.

## Placeholder metadata

- Path: `dist-windows/medwatch-backend.exe`
- Size: 262944 bytes (257 KiB)
- SHA256: `77c6281250abc2faa0fe51dbee12620b4c60e639e073198ac1bb5722fba67371`
- Architecture: PE32+ executable (console) x86-64, for MS Windows, 19 sections
- Build toolchain: `dockcross/windows-static-x64:latest` (MinGW-w64 GCC 11.4.0, static link)
- Runtime behavior: prints diagnostic message to stderr, opens MessageBoxA, returns exit code 1.
