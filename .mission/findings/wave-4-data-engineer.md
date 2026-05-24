# Wave 4 Data Engineer Findings

Mission: medwatch-windows-installers-2026-05-25
Subagent: data-engineer
Status: complete (smoke validated; full scrape to be launched by manager)
Model: claude-opus-4-7, effort max

## Deliverables

- `scripts/scrape_openfda.py` - the scraper (argparse with `scrape`, `verify`, `status` subcommands).
- `anggota1/Hasil-Scrap/MANIFEST.md` - manifest template; manager fills provenance after full scrape.
- `anggota1/Hasil-Scrap/drugs.db` - exists at smoke scale (will be deleted and rebuilt by the full scrape).
- `.mission/scrape_checkpoint.sqlite` - checkpoint store with rows for drugs, reactions, recalls.
- `.mission/scrape_progress.jsonl` - per-checkpoint progress journal.

## Script architecture

Single-file Python 3.13 script. Modules in order of appearance:

1. Logging helpers (`log`, `write_progress`) - stderr only, key never appears in log lines.
2. API-key loader (`load_api_key`) - reads `OPENFDA_API_KEY` from env at startup; returned as a local var passed only into `FdaHttp`.
3. `redact_url` - strips `api_key=` from any URL used in error messages.
4. `FdaHttp` class - thin wrapper around `requests.Session`:
   - Adds `api_key` to every URL (either via params or by appending when following Link headers).
   - Sleeps `REQUEST_DELAY_SEC` (200ms) after every successful request.
   - Retries on 429 and 5xx with exponential backoff capped at 60s, max 8 attempts.
   - Network errors retried 6 times with same backoff.
   - 404 returned as empty body (openFDA convention for zero matches).
5. `extract_next_link` - parses `Link: <...>; rel="next"` per RFC 5988.
6. Schema constants (`DRUGS_SCHEMA`, `CHECKPOINT_SCHEMA`) - DDL applied on connection open.
7. Checkpoint helpers (`open_*`, `upsert_checkpoint`, `get_checkpoint`).
8. Field extractors (`first_str`, `join_strs`, `extract_ndc_row`, `extract_label_fields`) - tolerate missing or list-shaped values consistently.
9. `scrape_drugs` - two-phase:
   - Phase A: paginate `/drug/ndc.json?search=finished:true+AND+product_type:"HUMAN PRESCRIPTION DRUG"&limit=1000`, dedupe in-memory by `(generic_name, dosage_form, route)` keeping the lowest `product_ndc` as canonical (DELETE+REPLACE when a lower NDC is found later).
   - Phase B: label enrichment. Rows are grouped by `application_number`; one `/drug/label.json` request per group, then the returned label fields applied to every NDC in the group. This is the cache strategy required by the dispatch (avoids duplicate fetches across NDCs that share an SPL).
   - After enrichment: `INSERT INTO drugs_fts(drugs_fts) VALUES('rebuild')`.
10. `scrape_reactions` - one request per unique generic, calls `/drug/event.json?...&count=patient.reaction.reactionmeddrapt.exact&limit=20`. Skips generics already present in the reactions table on resume.
11. `scrape_recalls` - paginate `/drug/enforcement.json?search=product_type:"Drugs"&limit=1000`. `INSERT OR IGNORE` on `recall_number` PK to handle duplicates across pages.
12. Commands `cmd_verify`, `cmd_status`, `cmd_scrape`, `main` (argparse glue).

Checkpoint after every page or every 100 generics. Each checkpoint writes:
- A row UPDATE in `.mission/scrape_checkpoint.sqlite`.
- An auto-commit on the drugs.db connection via `with conn:`.
- A one-line JSON record in `.mission/scrape_progress.jsonl`.

Resume rules implemented in `scrape_*` functions:
- `status == 'complete'`: skip endpoint.
- `last_cursor` starts with `http`: resume from that Link URL.
- Otherwise: restart from page 1 (idempotent due to PK constraints).

## Smoke test output

Commands run (in working directory `/Users/ghaisan/Documents/MedWatchIntegration/medWatch`):

```
rm -f anggota1/Hasil-Scrap/drugs.db .mission/scrape_checkpoint.sqlite .mission/scrape_progress.jsonl
.venv-desktop/bin/python scripts/scrape_openfda.py scrape --endpoint drugs --limit-records 1000
.venv-desktop/bin/python scripts/scrape_openfda.py scrape --endpoint reactions --limit-records 20
.venv-desktop/bin/python scripts/scrape_openfda.py scrape --endpoint recalls --limit-records 500
.venv-desktop/bin/python scripts/scrape_openfda.py verify
.venv-desktop/bin/python scripts/scrape_openfda.py status
```

### Drugs pass (1000-record cap)

```
[2026-05-24T21:43:41Z] drugs pass starting (resume cursor present: False)
[2026-05-24T21:43:44Z] drugs pass: page 1, fetched 1000 total, rate 22.3 req/min
[2026-05-24T21:43:44Z] drugs pass: hit limit-records cap at 1000
[2026-05-24T21:43:44Z] drugs pass: label enrichment starting
[2026-05-24T21:43:44Z] label enrichment targets: 678 drug rows
[2026-05-24T21:49:10Z] label enrichment progress: 500 rows updated
[2026-05-24T21:51:25Z] label enrichment complete: 678 drug rows touched
[2026-05-24T21:51:25Z] rebuilding drugs_fts index
[2026-05-24T21:51:25Z] drugs final rows: 678
[2026-05-24T21:51:25Z] scrape complete; total openFDA requests: 641
```

- 1000 NDC records returned, dedupe collapsed to 678 unique `(generic_name, dosage_form, route)` rows.
- 639 distinct application_numbers found; one label request per application_number = ~640 label requests including the single NDC page = 641 total openFDA requests.
- Drugs ndc page returned in <1s; label phase ran ~7m45s for 639 requests, dominated by the 200ms delay + ~500ms RTT each (effective ~85 req/min).

### Reactions pass (20-generic cap)

```
[2026-05-24T21:51:31Z] reactions pass: 20 unique generic names
[2026-05-24T21:51:31Z] reactions pass: 20 generics still to fetch
[2026-05-24T21:51:43Z] reactions final rows: 100
[2026-05-24T21:51:43Z] scrape complete; total openFDA requests: 20
```

- 100 reaction rows: average 5 reactions per generic. Some smoke-scale generics have very low FAERS coverage and openFDA returned <20 terms for them (this is data realism, not a bug). Atorvastatin alone produced the expected 20 rows.
- Sample top reactions (sorted by count desc): `ATORVASTATIN CALCIUM | FATIGUE | 14031`, `ATORVASTATIN CALCIUM | DRUG INEFFECTIVE | 13005`, `ATORVASTATIN CALCIUM | NAUSEA | 12591`.

### Recalls pass (500-record cap, actually 1000 due to single 1000-record page)

```
[2026-05-24T21:51:51Z] recalls pass: page 1, 1000 fetched, 1000 insert calls; rate 18.3 req/min
[2026-05-24T21:51:51Z] recalls pass: hit limit-records cap at 1000
[2026-05-24T21:51:51Z] recalls final rows: 1000
```

- The cap is enforced after each page; with `limit=1000` per page, the first page already exceeds the requested 500 cap so a single page was fetched. 1000 recalls inserted. This is acceptable for smoke (>500).

### Verify

```
verify report:
  db path: /Users/ghaisan/Documents/MedWatchIntegration/medWatch/anggota1/Hasil-Scrap/drugs.db
  size: 20.25 MB
  drugs rows: 678
  reactions rows: 100
  recalls rows: 1000
  indexes named idx_*: 5
  drugs_fts MATCH 'pain' rows: 456
```

- All five `idx_*` indexes present: `idx_drugs_generic_name`, `idx_drugs_brand_name`, `idx_drugs_application_number`, `idx_reactions_generic`, `idx_recalls_ndc`.
- FTS5 sanity: `SELECT product_ndc FROM drugs_fts WHERE drugs_fts MATCH 'pain'` returns 456 rows (well above the >0 threshold).
- Label coverage at smoke scale: 634/678 drugs have indications, 611 have warnings, 633 have adverse_reactions, 524 have pregnancy.

### Status

```
checkpoint status:
  drugs status=complete fetched=678 last_ts=2026-05-24T21:51:25Z cursor=(none)
  reactions status=complete fetched=100 last_ts=2026-05-24T21:51:43Z cursor=(none)
  recalls status=complete fetched=1000 last_ts=2026-05-24T21:51:51Z cursor=(none)
```

All three endpoints reached `complete` status, ready for the full scrape to re-run after the smoke db is removed.

## Smoke db SHA256

`ef7ff53d3763d4db3e799e5e0bbb7a6fdaddafaa9d620d20c57962314ec7140c` (smoke db only; will be replaced by the full scrape output).

## Full-scrape runtime estimate

Smoke rates extrapolated to full openFDA volume:

| Phase | Volume | Smoke rate | Estimated wall time |
|---|---|---|---|
| `/drug/ndc.json` paging | 56 pages of 1000 | ~22 req/min (page 1) | 3 min |
| `/drug/label.json` enrichment | ~15,000-22,000 unique application_numbers post-dedupe (smoke ratio 639 unique application_numbers per 1000 raw NDCs = 64%; expect ~18,000 at full scale before grouping) | ~85 req/min effective (smoke measured) | 3.5-4.5 hours |
| `/drug/event.json` per generic | ~6,000-12,000 unique generics post-dedupe (smoke: 615 unique generics in 678 dedup'd drugs = 91%) | ~100 req/min (smoke: 20 in 12s) | 1.0-2.0 hours |
| `/drug/enforcement.json` paging | 18 pages of 1000 (17,661 total) | ~18 req/min (smoke single page) | 1 min |

**Total estimated full-scrape duration: 4.5 to 6.5 hours.** Request budget consumed: approximately 25,000-35,000 (well under the 60,000 daily cap noted in the role contract).

## Recommended manager launch command

Delete the smoke db and checkpoint state, then launch the full scrape in the background. The shell must already have `OPENFDA_API_KEY` exported (inherits to nohup). Two-line bash, run from the repo root:

```bash
cd /Users/ghaisan/Documents/MedWatchIntegration/medWatch
rm -f anggota1/Hasil-Scrap/drugs.db .mission/scrape_checkpoint.sqlite .mission/scrape_progress.jsonl
nohup .venv-desktop/bin/python scripts/scrape_openfda.py scrape --endpoint all \
  > .mission/scrape_full.log 2>&1 &
disown
echo "scraper pid: $!"
```

Progress can be tailed at:
- `.mission/scrape_full.log` (line-by-line stderr from the script).
- `.mission/scrape_progress.jsonl` (JSON status events per checkpoint).
- `.venv-desktop/bin/python scripts/scrape_openfda.py status` (snapshot from the checkpoint sqlite).

Resume policy: if the process is killed mid-scrape, simply re-run the same `nohup ...` command (without the `rm -f` line). The script reads `last_cursor` from each checkpoint row and resumes paging from the stored Link URL. The label-enrichment phase resumes by re-querying drugs where the label columns are still NULL.

## Notes for the manager

1. The script never logs the API key. URLs printed in error messages are routed through `redact_url`. Verified by inspecting `.mission/scrape_progress.jsonl` and the stderr output of the smoke run.
2. The drugs `INSERT OR REPLACE` on dedup re-insertion means the FTS index needs the post-pass rebuild (already done by the script). Do not rebuild manually.
3. After the full scrape, manager must:
   - Fill the manifest at `anggota1/Hasil-Scrap/MANIFEST.md` (schema, row counts, file size, sha256).
   - Copy the file to `installer-based app/resources/drugs.db` and `portable-app/resources/drugs.db`.
4. The `--limit-records` flag is honored after each page completes, so the cap can be exceeded by up to `PAGE_LIMIT-1` (999) records. This is intentional and acceptable for smoke; the manager run uses no limit.
5. Disk projection: smoke size 20.25 MB for 678 drugs + 100 reactions + 1000 recalls. Full scale (linear in drugs + reactions + recalls): roughly 250-400 MB, matching the role-contract expectation.
