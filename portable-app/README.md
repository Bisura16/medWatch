# MedWatch (Portable variant)

## Output

This variant builds a single file portable Windows executable. The artifact
produced is `dist/MedWatch-x.y.z-portable.exe`, where `x.y.z` matches the
version in `package.json`. No installation step is required; the user can
double click the file to launch the app.

## Build steps

1. Run `npm install` from this folder.
2. Run `npm run build:portable` to produce the portable executable.

Cross-compiling a Windows portable executable from macOS requires `wine`.
Install it via `brew install --cask wine-stable` before running the build
script on macOS.

## What this contains

The portable executable carries everything the application needs to run offline:

- Embedded Next.js static frontend (Wave 3).
- PyInstaller-bundled Flask backend (Wave 2).
- SQLite drug database (Wave 4) copied to the user data directory on first launch.

## First-run SmartScreen warning

Windows SmartScreen will warn on first run because the executable is not code
signed. Click `More info` then `Run anyway`. Code signing is out of scope for
this academic submission.

## Offline operation

All drug data ships in `drugs.db`. The app does not require internet access at
runtime. The local Flask backend serves the data to the embedded renderer over
a loopback HTTP port.

## Database location

On Windows the runtime database lives at `%APPDATA%\MedWatch\drugs.db`. On a
macOS dev run it lands in `~/Library/Application Support/MedWatch/drugs.db`.
The file is copied from the read only resources directory on first launch.

## Maintainer

Ghaisan Khoirul Badruzaman <ghaisan.khoirul.b@gmail.com>
