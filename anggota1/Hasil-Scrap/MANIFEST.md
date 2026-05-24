# anggota1/Hasil-Scrap/drugs.db Manifest

Mission: medwatch-windows-installers-2026-05-25
Wave: 4 (openFDA prescription drug scrape)

## Provenance

(To be filled by the manager after the full scrape completes.)

## Source

openFDA API base: https://api.fda.gov
Endpoints used: drug/ndc.json (with finished:true AND product_type:HUMAN PRESCRIPTION DRUG), drug/label.json (per-NDC enrichment), drug/event.json (count by generic_name reactions), drug/enforcement.json (drug recalls).

## Schema

(Schema description here, derived from sqlite3 .schema output.)

## Row counts

(Counts here, derived from SELECT COUNT(*) FROM each table.)

## File size

(Size here.)

## SHA256

(SHA256 here.)
