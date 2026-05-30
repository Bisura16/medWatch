# anggota1/Hasil-Scrap/drugs.db Manifest

Component: MedWatch Windows installer data bundle
Stage: openFDA prescription drug scrape

## Provenance

Scrape executed on 2026-05-24 21:55 UTC to 2026-05-25 00:03 UTC by `scripts/scrape_openfda.py` (script SHA tracked in the git history at commit `82d9809`). Approximate wall clock: 2 hours 8 minutes.

Total openFDA requests spent: 12,865 (well under the 60,000 daily budget; under the 120,000 daily authenticated limit).

Source data fetched live from the public openFDA API on that date. The API key was supplied via the `OPENFDA_API_KEY` environment variable on the scrape host and is never written to disk, the database, the manifest, the script source, or any commit message.

## Source

openFDA API base: https://api.fda.gov

Endpoints used:
- `drug/ndc.json` with filter `finished:true AND product_type:"HUMAN PRESCRIPTION DRUG"` for the initial drug enumeration (55,666 raw NDC records before dedupe).
- `drug/label.json` with filter `openfda.product_ndc.exact:"<NDC>"` for per-drug label enrichment (indications, contraindications, warnings, adverse_reactions, dosage_and_administration, pregnancy, pediatric_use). Cached by `application_number` to avoid duplicate fetches across NDCs that share an SPL.
- `drug/event.json` with `count=patient.reaction.reactionmeddrapt.exact&limit=20` for the per-generic top-20 reaction aggregation.
- `drug/enforcement.json` with `product_type:"Drugs"` for recall enumeration.

Dedupe rule: drugs are deduplicated by the composite key `(generic_name, dosage_form, route)`. For each group, the row with the lexicographically lowest `product_ndc` is retained as canonical.

## Schema

```sql
PRAGMA journal_mode=WAL;

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
  product_type TEXT,
  scraped_at TEXT
);
CREATE INDEX idx_drugs_generic_name ON drugs(generic_name);
CREATE INDEX idx_drugs_brand_name ON drugs(brand_name);
CREATE INDEX idx_drugs_application_number ON drugs(application_number);

CREATE TABLE reactions (
  generic_name TEXT,
  reaction_term TEXT,
  count INTEGER,
  scraped_at TEXT,
  PRIMARY KEY (generic_name, reaction_term)
);
CREATE INDEX idx_reactions_generic ON reactions(generic_name);

CREATE TABLE recalls (
  recall_number TEXT PRIMARY KEY,
  product_ndc TEXT,
  classification TEXT,
  status TEXT,
  reason TEXT,
  recall_initiation_date TEXT,
  scraped_at TEXT
);
CREATE INDEX idx_recalls_ndc ON recalls(product_ndc);

CREATE VIRTUAL TABLE drugs_fts USING fts5(
  product_ndc UNINDEXED,
  brand_name,
  generic_name,
  indications,
  contraindications,
  warnings,
  adverse_reactions,
  content='drugs',
  content_rowid='rowid'
);
```

## Row counts

| Table | Rows |
|-------|------|
| drugs | 8,678 |
| drugs (with label data) | 8,522 (98.2 percent coverage) |
| reactions | 17,868 |
| recalls | 17,660 |
| drugs_fts MATCH 'pain' (sanity sample) | 5,816 |

## File size

237 MiB (248,684,544 bytes) for the `.db` file proper after FTS5 rebuild. WAL and SHM auxiliary files are absent after a clean `VACUUM`-equivalent close.

## SHA256

`76be06d65ada4ac13dc17786a76214d36fc496ba08d3222aff1b4660f86b0bae`

## Distribution

The file is excluded from git (per `.gitignore`) because it exceeds the 100 MiB hard cap on individual files in GitHub remotes. It is bundled into the two Electron installer variants via electron-builder `extraResources`. The canonical copy at `anggota1/Hasil-Scrap/drugs.db` is the source of truth for re-builds; the two variant copies at `installer-based app/resources/drugs.db` and `portable-app/resources/drugs.db` are byte-identical copies (same SHA256).

For external publication outside the installer bundles, attach the file to a GitHub Release in the `Bisura16/medWatch` repo with the SHA256 above included in the release notes.

## Reproducing the scrape

```bash
cd /path/to/medWatch
.venv-desktop/bin/python scripts/scrape_openfda.py scrape --endpoint all
.venv-desktop/bin/python scripts/scrape_openfda.py verify
```

`OPENFDA_API_KEY` must be exported in the launching shell. The script is resumable from its local scrape checkpoint database.

## License and attribution

openFDA data is in the public domain. See https://open.fda.gov/license/ for the canonical license statement. The dataset must not be used as a substitute for direct clinical judgment.
