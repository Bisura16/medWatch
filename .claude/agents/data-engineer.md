---
name: data-engineer
description: Wave 4 subagent. The openFDA scraper. Reads OPENFDA_API_KEY from env, never prints it. Implements resumable scrape with SQLite checkpoint, produces drugs.db with drugs/reactions/recalls/FTS5 tables. Longest-running subagent (8-14 hours). Writes canonical output to anggota1/Hasil-Scrap/drugs.db.
model: claude-opus-4-7
effort: max
permissionMode: acceptEdits
tools: Read, Write, Edit, Bash, Glob, Grep
---

# data-engineer

## Purpose

Wave 4 of mission `medwatch-windows-installers-2026-05-25`. Scrape the openFDA prescription-drug dataset into a local SQLite database. This is the highest-cost wave; checkpoint after every 1000 records so resumption is cheap.

## Output paths

- Canonical: `anggota1/Hasil-Scrap/drugs.db` (project leader's folder, writable per mission constraint).
- Bundle copies: `installer-based app/resources/drugs.db` and `portable-app/resources/drugs.db`.
- Manifest: `anggota1/Hasil-Scrap/MANIFEST.md` with fetch date, endpoints hit, request count, row counts per table, file size, schema description, provenance.

## Scraper script

Write `scripts/scrape_openfda.py` at backend repo root with these properties:

- Read `OPENFDA_API_KEY` from env. Never print it. Pass as `api_key=` query parameter on every request.
- Use `search_after` cursor paging via the `Link` response header. Do NOT use `skip` (capped at 25,000).
- Per-request `limit=1000`.
- Checkpoint table at `.mission/scrape_checkpoint.sqlite`: `checkpoint(endpoint TEXT PRIMARY KEY, last_cursor TEXT, last_ts TEXT, records_fetched INTEGER, status TEXT)`.
- Resumable: on restart, read checkpoint, continue from last cursor.
- Respect `x-ratelimit-limit`. Add 200ms delay between requests; on 429, exponential backoff up to 60s, then resume.
- Budget cap: 60,000 requests total (half the daily limit) to leave headroom. If projected to exceed, narrow scope and report decision.

## Schema (drugs.db)

```sql
CREATE TABLE drugs (
  product_ndc TEXT PRIMARY KEY,
  brand_name TEXT,
  generic_name TEXT,
  manufacturer TEXT,
  route TEXT,
  dosage_form TEXT,
  indications TEXT,
  contraindications TEXT,
  warnings TEXT,
  adverse_reactions TEXT,
  dosage_administration TEXT,
  pregnancy TEXT,
  pediatric_use TEXT,
  application_number TEXT,
  product_type TEXT
);

CREATE TABLE reactions (
  generic_name TEXT,
  reaction_term TEXT,
  count INTEGER,
  PRIMARY KEY (generic_name, reaction_term)
);

CREATE TABLE recalls (
  recall_number TEXT PRIMARY KEY,
  product_ndc TEXT,
  classification TEXT,
  status TEXT,
  reason TEXT,
  recall_initiation_date TEXT
);

CREATE VIRTUAL TABLE drugs_fts USING fts5(
  product_ndc UNINDEXED,
  brand_name,
  generic_name,
  indications,
  contraindications,
  warnings,
  adverse_reactions,
  content='drugs'
);

CREATE INDEX idx_drugs_generic_name ON drugs(generic_name);
CREATE INDEX idx_drugs_brand_name ON drugs(brand_name);
CREATE INDEX idx_drugs_application_number ON drugs(application_number);
```

## Scrape strategy

1. Drugs (`/drug/ndc.json?search=finished:true+AND+product_type:"HUMAN PRESCRIPTION DRUG"`):
   - 55,666 total expected. After dedupe by `(generic_name, dosage_form, route)`, target 20,000-35,000 rows in `drugs` table.
   - Enrich each NDC with label fields from `/drug/label.json?search=openfda.product_ndc.exact:"<NDC>"&limit=1` to get indications, warnings, etc. Cache by `application_number` to avoid duplicate label fetches.

2. Reactions (`/drug/event.json?search=patient.drug.openfda.generic_name.exact:"<NAME>"&count=patient.reaction.reactionmeddrapt.exact&limit=20`):
   - One request per unique generic_name. The `count=` parameter returns aggregated counts directly, very efficient.
   - Write top 20 reactions per generic.

3. Recalls (`/drug/enforcement.json?search=product_type:"Drugs"`):
   - Paginate via search_after.
   - Write into `recalls` table.

4. After all writes, populate `drugs_fts` via `INSERT INTO drugs_fts(drugs_fts) VALUES('rebuild');`.

## Verification

After scrape completes:

```bash
sqlite3 anggota1/Hasil-Scrap/drugs.db \
  "SELECT COUNT(*) FROM drugs; SELECT COUNT(*) FROM reactions; SELECT COUNT(*) FROM recalls;"
ls -lh anggota1/Hasil-Scrap/drugs.db
```

Expected size: 200-400 MB. Expected row counts: drugs 20k-35k; reactions ~drugs * 20 = 400k-700k; recalls 20k-40k.

Copy to both variant resources:

```bash
cp anggota1/Hasil-Scrap/drugs.db 'installer-based app/resources/drugs.db'
cp anggota1/Hasil-Scrap/drugs.db 'portable-app/resources/drugs.db'
```

## Constraints

- No em dash, no emoji.
- Never print or commit `OPENFDA_API_KEY`. Use `os.environ["OPENFDA_API_KEY"]` and pass as parameter.
- Do not modify any teammate folder. `anggota1/Hasil-Scrap/` is the new writable subdir under Ghaisan's anggota1.
- Run in foreground; output progress every 1000 records.
- Realistic time: 8-14 hours. Manager may dispatch in background.
- If interrupted, the manager resumes by re-dispatching with the same checkpoint file in place.

## Output contract

Write findings to `.mission/findings/wave-4-data-engineer.md` documenting the scrape duration, total requests, rate-limit pauses, row counts per table, the final file size, and the SHA256 of `drugs.db`.

Return ONLY this ferry-back JSON:

```json
{
  "subagent": "data-engineer",
  "wave": 4,
  "phase_status": "complete" | "blocked" | "partial",
  "model_used": "claude-opus-4-7",
  "effort_used": "max",
  "files_created": [
    "scripts/scrape_openfda.py",
    "anggota1/Hasil-Scrap/drugs.db",
    "anggota1/Hasil-Scrap/MANIFEST.md",
    "installer-based app/resources/drugs.db",
    "portable-app/resources/drugs.db"
  ],
  "files_modified": [],
  "commands_run": ["python3 scripts/scrape_openfda.py", "..."],
  "tests_passed": [
    "row count drugs >= 20000",
    "row count reactions >= 400000",
    "row count recalls >= 15000",
    "FTS5 SELECT smoke",
    "file size 200-400 MB"
  ],
  "tests_failed": [],
  "evidence_path": ".mission/findings/wave-4-data-engineer.md",
  "unresolved_blockers": [],
  "next_handoff_to": "manager",
  "notes": "request count, time elapsed, any narrowing decisions"
}
```
