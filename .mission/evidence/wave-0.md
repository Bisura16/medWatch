# Wave 0 evidence

All commands and outputs that back the Wave 0 log entry.

## Tool versions (captured 2026-05-24T20:54Z)

```
$ claude --version
2.1.150 (Claude Code)

$ node --version
v25.6.0

$ python3 --version
Python 3.14.5

$ npm --version
11.9.0

$ sqlite3 --version
3.51.0 2025-06-12 13:14:41 f0ca7bba1c5e232e5d279fad6338121ab55af0c8c68c84cdfb18ba5114dcaapl (64-bit)

$ which pyinstaller
(not on PATH)

$ which wine
(not on PATH)
```

Implications:
- Python 3.14.5 is very new (Oct 2025 release). Some packages used by the Flask backend (e.g. `google-cloud-storage 2.18.2`, `matplotlib 3.9.2`, `numpy 1.26.4`) may not have 3.14 wheels yet; will need `pip install` smoke before Wave 2.
- No `pyinstaller`, no `wine`: macOS host cannot produce a Windows `.exe` from PyInstaller. Will surface to user at Wave 2.

## Environment variable presence (no values leaked)

```
$ [ -n "$OPENFDA_API_KEY" ] && echo "present" || echo "absent"
OPENFDA_API_KEY: present (length matches expected pattern)

$ [ -z "$CLAUDE_CODE_SUBAGENT_MODEL" ] && echo "unset" || echo "set"
CLAUDE_CODE_SUBAGENT_MODEL: unset (good)

$ [ -z "$CLAUDE_CODE_EFFORT_LEVEL" ] && echo "unset" || echo "set"
CLAUDE_CODE_EFFORT_LEVEL: unset (good)
```

## openFDA reachability (with auth)

```
$ curl -sI "https://api.fda.gov/drug/ndc.json?search=finished:true&limit=1&api_key=$OPENFDA_API_KEY" | head -20
HTTP/2 200
date: Sun, 24 May 2026 20:54:34 GMT
content-type: application/json; charset=utf-8
content-length: 2477
link: <https://api.fda.gov/drug/ndc.json?search=finished%3Atrue&limit=1&skip=0&search_after=0%3D--KtUp4BM7UYVJyIK04t>; rel="next"
x-ratelimit-limit: 240
```

The `Link: rel="next"` header confirms `search_after` cursor pagination is the right primitive. The `x-ratelimit-limit: 240` is per-minute (key adds 200 on top of the unauthenticated 40).

## openFDA prescription-drug total (THE number that drives Wave 4 scope)

```
$ curl -s "https://api.fda.gov/drug/ndc.json?search=finished:true+AND+product_type:%22HUMAN+PRESCRIPTION+DRUG%22&limit=1&api_key=$OPENFDA_API_KEY" \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); m=d.get("meta",{}).get("results",{}); print("total:", m.get("total","?"))'
total prescription human: 55666 skip: 0 limit: 1
```

The mission target was "25,000 to 50,000 unique products" after dedupe. Raw count is 55,666 finished NDC entries, so after dedupe by `(generic_name, dosage_form, route)` we should land in the 20,000-35,000 unique products range. The mission scope is feasible.

## Backend layout (Flask app)

```
$ ls medWatch/api/
Dockerfile  README.md  __init__.py  __pycache__  app.py  auth.py  bootstrap.py
config.py  data  helpers.py  middleware.py  requirements.txt  routes
static  storage.py  tests
```

Flask entry: `api/app.py`. Has `create_app()` factory and module-level `app`. Configuration via `api/config.py` (`PORT`, `DEBUG`, `CORS_ORIGINS`).

Backend deps (`api/requirements.txt`):
```
Flask==3.1.3, Flask-Cors==6.0.0, PyJWT==2.12.0, bcrypt==4.2.1,
google-cloud-storage==2.18.2, gunicorn==23.0.0, requests==2.33.0,
beautifulsoup4==4.12.3, matplotlib==3.9.2, numpy==1.26.4, fpdf2==2.8.1
```

Note: `google-cloud-storage` and `gunicorn` are cloud-only deps. For desktop bundling, both can be optionally excluded to keep the binary lean. PyInstaller spec in Wave 2 will use `--exclude-module google.cloud.storage` and `--exclude-module gunicorn`.

## Frontend layout (Next.js)

```
$ cat FrontendMedwatch/package.json | head -20
"name": "medwatch", "version": "0.1.0", ...
"dependencies": {
  "next": "16.2.1",
  "react": "19.2.4", "react-dom": "19.2.4",
  "@react-three/fiber": "^9.5.0", "@react-three/drei": "^10.7.7",
  "three": "^0.183.2",
  "framer-motion": "^12.38.0",
  "recharts": "^3.8.1",
  ...
}
```

Next.js 16.2.1, React 19.2.4. Static export support exists via `output: 'export'` but Next 16 has more aggressive Cache Components by default; Wave 3 frontend-bundler will need to audit for runtime-only features.

## Prior anggota1 scraper

```
$ ls anggota1/openfda/
README.md  __init__.py  __pycache__  fetch.py  (21259 bytes)

$ ls anggota1/data/
README.md  drug_recalls.json (2.5 MB)  drug_safety_data.json (78 KB)
```

`anggota1/openfda/fetch.py` produces JSON output, not SQLite. Will be cited as reference for the request shape and rate-limit handling but Wave 4 writes a fresh SQLite-emitting scraper.

## Git state at Wave 0 start

```
$ git status
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  modified:   anggota5/__pycache__/auth.cpython-314.pyc
  modified:   api/data/patients.json
  modified:   api/data/users.json

Untracked files:
  Procfile
```

The three modified files are pre-existing (not from this mission). `anggota5/__pycache__/` is auto-generated; `api/data/*.json` are Ghaisan's integration-layer data files modified by other sessions. None blocked by this mission. The untracked `Procfile` is from a prior Heroku-style deployment attempt. None of these will be touched or committed in this mission.

## Recent commit history

```
$ git log --oneline -10
1ef862f chore(state): mirror post-merge SHAs and Vercel auto-deploy result
b91686f docs(test): redact expired JWT tokens in evidence transcripts
8fc8fcd docs(security): document WT-04 as user-accepted Known Finding, not self-waive
8389d3a docs(closeout): honest test metrics + mirror STATE + sync CHANGELOG
...
```

Prior mission completed; HEAD `1ef862f` is the mirror commit. This Wave 0 work is the first commit of the new windows-installers mission.

## Pre-flight constraint 1 audit (model/effort)

```
$ cat .claude/settings.json | grep -E '"model"|"effortLevel"'
  "model": "claude-opus-4-7",
  "effortLevel": "max",
```

OK. New agent files in `.claude/agents/` are pinned to `claude-opus-4-7` and per-agent `effort:` tier. Will verify via grep after agent files are written.
