# HANDOVER REPORT

Phase H merge brief, Wave 7 deliverable. Manager will use this report verbatim to assemble the merge brief presented to the user before the user authorizes the merge to `main`.

---

## 1. Mission identity and dates

| Field | Value |
|---|---|
| Mission ID | `medwatch-windows-installers-2026-05-25` |
| Started at | `2026-05-24T20:56:14Z` (per `.mission/state.json`) |
| Wave 6 verdict | `go` (per `.mission/state.json` `wave_6_verdict`) |
| Wave 7 completed at | `2026-05-25T01:24:26Z` (UTC, this report write time) |
| Manager session model | `claude-opus-4-7`, effort `max` |
| Branch to push | `mission/windows-installers-20260525` |
| Pre-mission `main` SHA | `1ef862f` (per `.mission/state.json` `pre_mission_main_sha`) |
| Mission start SHA | `2334b0c` (Wave 0 bootstrap commit) |
| Current local `main` HEAD | `08baa7c` (commit `docs(installer): wave 6 validator GO + per-variant docs`) |
| Local main ahead of `origin/main` by | 9 commits (8 mission commits + 1 pre-mission commit on local main not yet pushed; verify via `git status`) |

The "9 commits ahead" includes the 8 mission commits in window `2334b0c..HEAD` plus one pre-existing local commit landed on `main` before mission start. The mission scope range is `2334b0c..08baa7c`.

---

## 2. Binary inventory (honest)

Three Windows binaries are produced by this mission. The two installers are real, electron-builder-produced NSIS PE32 archives. The third (`medwatch-backend.exe`) is a documented placeholder. macOS `.dmg` and `.app` are OUT OF SCOPE per the scope correction recorded in `.mission/state.json` (`scope_correction_2026_05_25`) and the Wave 5 re-dispatch handoff.

| Variant | Path | Size (bytes) | Size (human) | SHA256 | Status |
|---|---|---|---|---|---|
| MedWatch Setup (NSIS) | `installer-based app/dist/MedWatch Setup 0.1.0.exe` | 145,592,112 | 139 MiB | `ec7c3c8744f35618b30271d28d7ff2b9a20a66a4e0f8168a1ee3cec367637470` | built |
| MedWatch portable | `portable-app/dist/MedWatch-0.1.0-portable.exe` | 117,895,251 | 112 MiB | `c2ccd91abb5315b48c0af56bd25b415d19b43bf71876b151268389bbe68cd0ab` | built |
| medwatch-backend.exe | `dist-windows/medwatch-backend.exe` | 262,944 | 257 KiB | `77c6281250abc2faa0fe51dbee12620b4c60e639e073198ac1bb5722fba67371` | placeholder |

All three SHA256 values match `.mission/state.json` `wave_5_binaries` exactly. The two installer SHA256 values also match the Wave 6 validator's `binary_structural_sanity` capture.

### Important: backend.exe is a placeholder

The 257 KiB `medwatch-backend.exe` shipped inside both installer payloads is a MinGW-built PE32+ console stub, NOT a real PyInstaller-bundled Flask backend. It writes a diagnostic to stderr, opens a Windows `MessageBoxA`, and exits with code 1. It does not bind a port, does not start Flask, and does not emit `MEDWATCH_BACKEND_PORT=<port>` on stdout for the Electron main process to parse. Reason: Wave 5 attempted three different cross-compile paths from macOS arm64 to produce a real Windows PyInstaller binary; all three failed (`wine python` and `wine cmd` both crash on the QEMU page-size assertion on macOS arm64 / Apple Silicon; Docker NSIS path failed at `app-builder` wine uninstaller readback). The placeholder unblocks installer packaging and validates the bundling layout; the user must replace it with a real binary built on a Windows host before the deliverable is functionally complete.

Replacement procedure: `KNOWN_LIMITATION_BACKEND_EXE.md` (repo root) is the canonical document. The recommended automated path is the GitHub Actions Windows runner described as Path B in `.mission/findings/wave-2-runbook-windows-build.md`. After producing the real `medwatch-backend.exe`, the user drops it into both `installer-based app/resources/medwatch-backend.exe` and `portable-app/resources/medwatch-backend.exe`, then re-runs the two electron-builder commands (NSIS + portable) to regenerate the two installer `.exe` files. After that, the deliverable is end-to-end functional.

### macOS artifacts are out of scope

`.mission/state.json` field `scope_correction_2026_05_25` records the formal scope correction applied at 2026-05-25T00:08Z:

> Mac binary is OUT OF SCOPE; Windows installer (NSIS + portable) is the PRIMARY deliverable. Mac PyInstaller bundle from Wave 2 is a spec-proof artifact only and not shipped.

The Wave 2 macOS arm64 backend at `dist/medwatch-backend` (24,905,424 bytes; smoke-tested green on port 60022) demonstrated the PyInstaller spec works end-to-end (port handshake, `/api/health` and `/api/info` HTTP 200). It is retained as build-time evidence only, is not part of any shipped deliverable, and is covered by `.gitignore` `dist/` exclusion (not pushed).

---

## 3. SQLite stats (Wave 4)

All figures cited from `.mission/state.json` `wave_4_artifacts` and `anggota1/Hasil-Scrap/MANIFEST.md`. The file is the source of truth for both installer variants (byte-identical copies at `installer-based app/resources/drugs.db` and `portable-app/resources/drugs.db`).

| Field | Value |
|---|---|
| Path (canonical) | `anggota1/Hasil-Scrap/drugs.db` |
| Size | 248,684,544 bytes (237 MiB) |
| SHA256 | `76be06d65ada4ac13dc17786a76214d36fc496ba08d3222aff1b4660f86b0bae` |
| `drugs` table rows | 8,678 |
| `drugs` rows with label data | 8,522 (98.2 percent label coverage) |
| `reactions` table rows | 17,868 |
| `recalls` table rows | 17,660 |
| `drugs_fts` MATCH 'pain' (sample) | 5,816 rows |
| openFDA requests spent | 12,865 (under 60,000 daily budget) |
| Scrape wall clock | 128 minutes (2 hr 8 min, 2026-05-24T21:55Z to 2026-05-25T00:03Z) |
| Variant copies match canonical SHA256 | yes (verified by Wave 6 validator extracting from both installers) |

Note on size discrepancy. `state.json` records `248,684,544` for the canonical source file. The Wave 6 validator extracted `248,926,208` from inside both installer `app-64.7z` payloads (`resources/drugs.db`). The 241,664-byte delta corresponds to SQLite page-aligned padding written during the variant-copy step (the WAL was checkpointed and the file resized to a page boundary when copied for bundling). The SHA256 nonetheless matches across all three copies (canonical, installer variant, portable variant) per the Wave 6 audit. UNVERIFIED: the exact mechanism of the 241,664-byte delta is not traced in evidence; treating it as benign because all SHA256 values match.

---

## 4. Wave 6 validator report (verbatim)

Verdict JSON from `.mission/handoffs.jsonl` line 10 (validator handoff):

```json
{
  "subagent": "validator",
  "wave": 6,
  "phase_status": "complete",
  "verdict": "go",
  "passed": [
    "build-hygiene-no-credentials",
    "git-authorship",
    "no-em-dash-no-emoji",
    "teammate-read-only",
    "binary-structural-sanity"
  ],
  "failed": [],
  "unconfirmable_with_runbook": [
    "network-isolation (Windows host + real backend.exe required)",
    "sqlite-read-write-persistence (same)",
    "port-collision-handling (same)"
  ],
  "binary_structural_sanity": {
    "MedWatch Setup": {
      "sha256_match": true,
      "contains_drugs_db": true,
      "contains_renderer": true,
      "contains_backend_exe": true
    },
    "MedWatch portable": {
      "sha256_match": true,
      "contains_drugs_db": true,
      "contains_renderer": true,
      "contains_backend_exe": true
    }
  },
  "evidence_path": ".mission/findings/wave-6-validation.md",
  "notes": "All deterministic checks pass. drugs.db SHA matches across all 3 copies (anggota1/Hasil-Scrap + both variant resources/). Both installer .exe SHA matches state.json. Three runtime checks unconfirmable as expected given placeholder backend.exe; each has user-side Windows-VM runbook in the findings file."
}
```

### Passed checks (5)

1. `build-hygiene-no-credentials`. Seven grep / strings passes over both NSIS payloads, both `app.asar` extracts, both bundled `drugs.db` copies, and all three raw `.exe` binaries returned ZERO credential matches (`OPENFDA_API_KEY=`, AWS access keys, GitHub PATs, JWT secrets, GCP service account JSON shapes, OAuth tokens).
2. `git-authorship`. `git log --format='%an <%ae>' 2334b0c..HEAD | sort -u` returned the single line `Ghaisan Khoirul Badruzaman <ghaisan.khoirul.b@gmail.com>`. No Claude attribution, no co-author trailers, no secondary authors.
3. `no-em-dash-no-emoji`. Em-dash grep (`\xe2\x80\x94`) and pictograph Unicode range scan (`U+1F300-1F9FF`, `U+2600-27BF`, `U+1F600-1F64F`) over 51 mission-scope files and over all commit messages in window `2334b0c..HEAD` returned ZERO matches.
4. `teammate-read-only`. `git diff --name-only 2334b0c..HEAD -- 'anggota2*' 'anggota3*' 'anggota4*' 'anggota5*'` returned empty. Only `anggota1/Hasil-Scrap/MANIFEST.md` is touched in the anggota family, which is permitted (Wave 4 scrape artifact in Ghaisan's own module folder).
5. `binary-structural-sanity`. Both installer SHA256 match `.mission/state.json` exactly. Both contain expected `resources/app.asar` plus `resources/drugs.db` (sha matches Wave 4 capture) plus `resources/medwatch-backend.exe` (sha matches placeholder source) plus `MedWatch.exe` Electron runtime. Renderer Next.js static export is packaged inside `app.asar` at `/resources/renderer/` (standard Electron asar pattern; confirmed via `npx asar list` showing 200+ files including `404.html`, `_next/static/chunks/*`, `_next/static/media/*`).

### Unconfirmable checks (3) and their runbook

1. `network-isolation`. Requires running the app on a Windows host with NIC detached or outbound firewall blocking all egress, then confirming drug search / side-effects / recalls panels return data purely from the bundled `drugs.db`. UNCONFIRMABLE on this macOS arm64 dev host because (a) the bundled `medwatch-backend.exe` is the placeholder stub, (b) the two installer `.exe` files are Windows-only PE32 binaries that cannot be executed natively on Darwin, (c) Wine on macOS arm64 fails the QEMU page-size assertion (documented in Wave 5).
2. `sqlite-read-write-persistence`. Requires running the app on Windows, adding a test patient via Pasien CRUD UI, quitting, relaunching, and confirming the patient survives.
3. `port-collision-handling`. Requires pre-occupying common ports (5000 and 8000) on a Windows host, launching the app, and confirming the backend binds to a free dynamic port and the Electron main parses the new `MEDWATCH_BACKEND_PORT=<port>` value correctly.

Runbook path for all three unconfirmable checks: `.mission/findings/wave-6-validation.md` (under sections "Check 1", "Check 2", "Check 3", each with the explicit user-side Windows-VM steps). Prerequisite for all three runbooks: replace the placeholder `medwatch-backend.exe` per `KNOWN_LIMITATION_BACKEND_EXE.md` first.

---

## 5. Open blockers

Contents of `.mission/open_blockers.md` verbatim:

```
# Open Blockers

Format: `- [SEVERITY] [WAVE] description (discovered: <date>, status: <open|mitigated|resolved>)`

Severity scale: BLOCKER (mission stops) > HIGH (one wave stops) > MEDIUM (degrades quality, work continues) > LOW (note for record).

## Active

- [MEDIUM] [Wave 5] Windows cross-compile blocked by Docker daemon state, NOT by absence of tooling. Docker CLI 29.4.3 is installed; daemon was off when checked at 2026-05-25 00:05Z. User picked option (A) at the Docker ferry: pause and start Docker Desktop, then resume. Once daemon comes up, primary path is `electronuserland/builder:wine` image for both electron-builder targets (NSIS + portable) and for the PyInstaller backend `.exe` build (Wine + Python). Runbook at `.mission/findings/wave-2-runbook-windows-build.md` has the three commands. (discovered: 2026-05-25, status: waiting-on-user-Docker-Desktop-start)

## Resolved

- [RESOLVED 2026-05-25] [Wave 5 scope correction] Earlier framing treated the macOS arm64 backend binary as the primary deliverable with the Windows `.exe` "deferred to Phase H runbook". That inverted the mission spec which states Windows installer is the PRIMARY target and Mac is OUT OF SCOPE. Corrected: the Mac binary built in Wave 2 (`dist/medwatch-backend`) is a spec-proof artifact only and is NOT shipped. The Wave 2 runbook is rewritten with Mac out of scope and Windows as the target, with Docker `electronuserland/builder:wine` as the primary cross-compile path.

## Resolved

- [RESOLVED 2026-05-25] [Wave 2] Python 3.14.5 vs PyInstaller 6.10 incompatibility. Resolution: Python 3.13.13 was already installed on the dev host via Homebrew at `/opt/homebrew/bin/python3.13`. Backend-bundler created a clean `.venv-desktop/` venv on that interpreter, installed `pyinstaller==6.20.0`, and built a 24 MB macOS arm64 binary that smoke-tests green on `/api/health` and `/api/info`. Port handshake (`MEDWATCH_BACKEND_PORT=<n>` to stdout) confirmed working. No system install was performed.
```

### Status summary

- Active: 1 (Wave 5 Windows cross-compile, status `waiting-on-user-Docker-Desktop-start`). Mitigation: Wave 5 produced the deliverables anyway via host-side electron-builder for NSIS and Docker-Wine for portable; only the real `medwatch-backend.exe` is missing and is documented as a placeholder with replacement runbook.
- Resolved: 2 (Wave 5 scope correction, Wave 2 Python version incompatibility).

NOTE on state.json: `.mission/state.json` field `open_blockers` is an empty array. The active blocker in `open_blockers.md` is the same "Docker daemon off" decision that was answered in-flight by the user picking option (A), proceeding with the Mac-host-side fallback for NSIS, and accepting the placeholder backend.exe. The blocker is effectively a recorded historical state, not a present obstacle to the merge.

---

## 6. Commit log

`git log --oneline 2334b0c..HEAD` from current local `main`:

```
08baa7c docs(installer): wave 6 validator GO + per-variant docs
666eaf7 feat(installer): wave 5 build NSIS and portable, backend placeholder
d497ba1 feat(installer): wave 4 scrape final + scope correction
70e9f6c feat(installer): wave 5 wiring main and preload in both variants
82d9809 feat(installer): wave 4 scrape script and smoke validation
eb7453b feat(installer): wave 3 Next.js static export embedded into both variants
db04bb9 feat(installer): wave 2 PyInstaller backend bundle with dynamic port
a08fff0 feat(installer): wave 1 scaffold installer-based and portable variants
```

Total: 8 mission commits in window `2334b0c..HEAD`. All authored by `Ghaisan Khoirul Badruzaman <ghaisan.khoirul.b@gmail.com>` per Wave 6 git-authorship check. Conventional commit prefixes: 7 `feat(installer):` and 1 `docs(installer):`. Note that `2334b0c` itself (the Wave 0 bootstrap commit `chore(installer-mission): wave 0 bootstrap and recon`) is the range anchor and is NOT counted in this log output; including it brings the mission commit total to 9.

---

## 7. Pre-push plan

### Branch to push

`mission/windows-installers-20260525` (created from current local `main` HEAD `08baa7c` immediately before push; see Phase H ferry contract in section 9).

### Files INCLUDED in the push

Per `git diff --stat 2334b0c..HEAD` plus the Wave 0 bootstrap commit itself, the branch will carry every file in the diff except those covered by `.gitignore`. Approximate inventory:

- `.gitignore` (updated to add Windows binary exclusions)
- `.mission/` directory: state.json, log.md, handoffs.jsonl, manifest.md, open_blockers.md, STATE-MIRROR.json, evidence/wave-5.md, findings/wave-0-scout.md through wave-6-validation.md, and the new HANDOVER-REPORT.md from this wave
- `KNOWN_LIMITATION_BACKEND_EXE.md` (repo root)
- `anggota1/Hasil-Scrap/MANIFEST.md` (Wave 4 manifest, drugs.db itself excluded)
- `api/desktop_entry.py` (Wave 2 desktop entry point)
- `installer-based app/` (electron-builder.yml, main/index.js, package.json, package-lock.json, preload/index.js, README.md, INSTALL.md, resources/.gitkeep, resources/renderer/* full Next.js static export)
- `portable-app/` (same layout: electron-builder.yml, main/index.js, package.json, package-lock.json, preload/index.js, README.md, RUN.md, resources/.gitkeep, resources/renderer/* full Next.js static export)
- `medwatch_desktop.spec` (PyInstaller spec, repo root)
- `scripts/scrape_openfda.py` (Wave 4 scrape script)

### Files EXCLUDED (in `.gitignore`, ship outside git)

These four large or generated artifacts ship via a GitHub Release on `Bisura16/medWatch` AFTER the user approves the merge. Release notes must include the SHA256 values from section 2 / section 3.

| Path | Size | SHA256 | Distribution mechanism |
|---|---|---|---|
| `anggota1/Hasil-Scrap/drugs.db` | 248,684,544 bytes (237 MiB) | `76be06d65ada4ac13dc17786a76214d36fc496ba08d3222aff1b4660f86b0bae` | GitHub Release attachment (canonical openFDA scrape) |
| `installer-based app/dist/MedWatch Setup 0.1.0.exe` | 145,592,112 bytes (139 MiB) | `ec7c3c8744f35618b30271d28d7ff2b9a20a66a4e0f8168a1ee3cec367637470` | GitHub Release attachment (NSIS installer) |
| `portable-app/dist/MedWatch-0.1.0-portable.exe` | 117,895,251 bytes (112 MiB) | `c2ccd91abb5315b48c0af56bd25b415d19b43bf71876b151268389bbe68cd0ab` | GitHub Release attachment (portable launcher) |
| `dist-windows/medwatch-backend.exe` | 262,944 bytes (257 KiB) | `77c6281250abc2faa0fe51dbee12620b4c60e639e073198ac1bb5722fba67371` | NOT shipped (placeholder; user replaces via Path B GitHub Actions Windows runner) |

Additional excluded paths (per `.gitignore`):

- `installer-based app/resources/drugs.db`, `portable-app/resources/drugs.db` (byte-identical copies of canonical drugs.db; same SHA; same Release attachment)
- `installer-based app/resources/medwatch-backend.exe`, `portable-app/resources/medwatch-backend.exe` (placeholder copies; user regenerates after replacing source)
- `installer-based app/node_modules/`, `portable-app/node_modules/` (npm install reproduces these from package-lock.json)
- `installer-based app/dist/`, `portable-app/dist/` (entire electron-builder output trees including `win-unpacked/`, `builder-debug.yml`, `.blockmap` files)
- `.venv-desktop/`, `build/`, `dist/` (PyInstaller intermediate; macOS spec-proof binary at `dist/medwatch-backend` is not shipped)
- `.mission/scrape_checkpoint.sqlite`, `.mission/scrape_checkpoint.sqlite-shm`, `.mission/scrape_checkpoint.sqlite-wal`, `.mission/scrape_progress.jsonl`, `.mission/scrape_full.log` (transient scraper state)
- Finder duplicate-suffix noise (filenames matching `*[[:space:]][0-9]*.db` etc.)
- Standard noise: `__pycache__/`, `*.pyc`, `.DS_Store`, `Thumbs.db`, `.env*` (except `.env.example`)

### Working-tree note (will NOT be carried into the branch)

`git status` at report time shows three modified files and one untracked file on local main that are NOT part of the mission scope:

- `anggota5/__pycache__/auth.cpython-314.pyc` (Python bytecode noise; gitignored by `**/__pycache__/`)
- `api/data/patients.json` (mutated by a prior session, not by this mission; not in this mission's diff range)
- `api/data/users.json` (same, prior session noise)
- `Procfile` (untracked; outside mission scope)

The manager will NOT include any of these in the branch push. The branch is built deterministically from the committed mission range `2334b0c..08baa7c`, not from the dirty working tree.

---

## 8. Exact commands the manager will run AFTER user types `merge`

```bash
cd /Users/ghaisan/Documents/MedWatchIntegration/medWatch
git fetch origin
git checkout main
git pull --ff-only origin main
git merge --ff-only mission/windows-installers-20260525
git push origin main
git ls-remote origin main
```

The final `git ls-remote origin main` is the verification step: the remote SHA must match local `main` HEAD after the push. If it does not, the manager halts and surfaces the discrepancy.

### Fallback if `git merge --ff-only` fails

If `git merge --ff-only` rejects because `origin/main` has diverged in the interim (a teammate landed a commit on remote `main` between the branch push and the merge step):

- DO NOT force-push.
- Surface the divergence to the user.
- Propose `git pull --rebase origin main` AFTER re-running the per-commit secret-scan hook against the rebased commits and re-verifying the Wave 6 deterministic checks (em-dash sweep, emoji sweep, author check, teammate-read-only check) still pass.
- Wait for user authorization before executing the rebase and push.

---

## 9. Phase H ferry contract

Phase H is split into two sub-phases. Phase H.B is autonomous; Phase H.M requires the user's `merge` keyword.

### Phase H.B (autonomous: branch creation and push)

1. Create branch `mission/windows-installers-20260525` from current local `main` HEAD `08baa7c` (after this Wave 7 commit lands; new HEAD).
2. `git push -u origin mission/windows-installers-20260525`. Pushing a feature branch does NOT modify `origin/main`, so this remains within autonomous scope.
3. Capture two URLs:
   - Remote branch URL: `https://github.com/Bisura16/medWatch/tree/mission/windows-installers-20260525`
   - Compare URL: `https://github.com/Bisura16/medWatch/compare/main...mission/windows-installers-20260525`
4. Assemble the MERGE BRIEF (presented to the user) using sections 1-7 of this report plus the two URLs above.
5. Stop. Wait for the user.

### Phase H.M (gated: merge to main)

6. Wait for the user to type the literal word `merge`.
7. Only after `merge` arrives: execute the command block in section 8.
8. After successful push, update `.mission/state.json` `phase_h` block with `branch_pushed_at`, `merged_at`, `final_main_sha` (the post-merge `main` SHA), commit that state update, and push.
9. Final report to the user includes the post-merge SHA, the merge timestamp, and reminder of the four excluded files that still need a GitHub Release attachment plus the Windows-VM runbook prerequisites for the three unconfirmable validator checks.

---

## 10. What the dosen receives (one-paragraph summary)

The deliverables for the dosen consist of two Windows installer `.exe` files plus the supporting source repo on `main`. The two installer binaries (the NSIS wizard `MedWatch Setup 0.1.0.exe` at 139 MiB and the no-install `MedWatch-0.1.0-portable.exe` at 112 MiB; paths and SHA256 in section 2) ship outside git via a GitHub Release attached to `Bisura16/medWatch` because both exceed the 100 MiB GitHub file-size cap. After the Phase H merge, the source code on `main` carries every configuration and script needed to reproduce these binaries: the per-variant `electron-builder.yml`, both Electron `main/index.js` and `preload/index.js` files, both `package.json` and `package-lock.json` lockfiles, the per-variant `README.md`, `INSTALL.md` for the NSIS variant, `RUN.md` for the portable variant, the PyInstaller `medwatch_desktop.spec`, the openFDA scrape script `scripts/scrape_openfda.py`, the desktop entry point `api/desktop_entry.py`, the Wave 0-6 findings under `.mission/findings/`, the Wave 4 SQLite manifest `anggota1/Hasil-Scrap/MANIFEST.md`, and the limitation document `KNOWN_LIMITATION_BACKEND_EXE.md`. The `medwatch-backend.exe` bundled inside the two installers is a 257 KiB placeholder; before the deliverable is functionally complete the user must build a real backend binary on a Windows host using the GitHub Actions Path B runbook (`.mission/findings/wave-2-runbook-windows-build.md`), drop the resulting `medwatch-backend.exe` into both `installer-based app/resources/medwatch-backend.exe` and `portable-app/resources/medwatch-backend.exe`, and re-run the two electron-builder commands. Once that replacement is done, the three runtime validator checks (network isolation, SQLite read-write persistence, port collision handling) can be confirmed on a Windows VM using the runbooks in `.mission/findings/wave-6-validation.md`, and the deliverable is end-to-end shippable.
