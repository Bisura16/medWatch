#!/usr/bin/env python3
"""Add and populate a presentation-only display_name column on drugs.db.

The catalog stores raw openFDA strings (often ALL CAPS multi-ingredient
generic names) that read like noise in a list. This migration precomputes
a clean display_name so the runtime can SELECT it directly without touching
the underlying rows.

Derivation priority (per the frozen contract):
    1. brand_name (openFDA harmonized)
    2. rxnorm_name (normalized generic)
    3. cleaned generic_name / ingredient string

Cleanup: collapse whitespace, title-case strings that are mostly uppercase,
and when the chosen name resolves to more than two ingredients show the first
ingredient plus "(kombinasi)". The full string stays available in the detail
view via the existing columns. No rows are added, removed, or otherwise
changed; only the new column is written. Idempotent and safe to re-run.

Usage:
    python scripts/migrate_display_name.py [db_path ...]

With no args it migrates the canonical dev catalog. Pass explicit paths to
migrate the bundled copies under the Electron resources dirs too.
"""
import re
import sqlite3
import sys
from pathlib import Path

EXPECTED_ROWS = 20828

_INGREDIENT_SPLIT = re.compile(r"\s+and\s+|[,/;+]", re.IGNORECASE)
_WS = re.compile(r"\s+")

DEFAULT_DBS = [
    "anggota1/Hasil-Scrap/drugs.db",
    "installer-based app/resources/drugs.db",
    "portable-app/resources/drugs.db",
]


def _clean(text):
    return _WS.sub(" ", (text or "").strip())


def _smart_title(s):
    """Clean a name for display: strip wrapping punctuation, title-case if it
    reads as SHOUTING (mostly uppercase), and ensure the first letter is upper.
    """
    s = s.strip(" .,;:/-()[]{}\t")
    letters = [c for c in s if c.isalpha()]
    if not letters:
        return s
    upper_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
    if upper_ratio > 0.7:
        s = s.title()
        # Keep common conjunctions lowercase for readability.
        s = re.sub(r"\bAnd\b", "and", s)
    if s and s[0].islower():
        s = s[0].upper() + s[1:]
    return s


def _collapse_combo(name):
    """If the name resolves to >2 ingredients, show the first + (kombinasi)."""
    parts = [p.strip() for p in _INGREDIENT_SPLIT.split(name) if p.strip()]
    if len(parts) > 2:
        return f"{parts[0]} (kombinasi)"
    return name


def derive_display_name(brand, rxnorm, generic):
    for src in (brand, rxnorm, generic):
        s = _clean(src)
        if s:
            return _collapse_combo(_smart_title(s))[:160] or "(tanpa nama)"
    return "(tanpa nama)"


def _column_exists(conn, table, column):
    return any(r[1] == column for r in conn.execute(f"PRAGMA table_info({table})"))


def migrate(db_path):
    p = Path(db_path)
    if not p.exists():
        print(f"SKIP (missing): {db_path}")
        return False
    conn = sqlite3.connect(str(p))
    try:
        before = conn.execute("SELECT COUNT(*) FROM drugs").fetchone()[0]
        if not _column_exists(conn, "drugs", "display_name"):
            conn.execute("ALTER TABLE drugs ADD COLUMN display_name TEXT")
        rows = conn.execute(
            "SELECT rowid, brand_name, rxnorm_name, generic_name FROM drugs"
        ).fetchall()
        conn.executemany(
            "UPDATE drugs SET display_name = ? WHERE rowid = ?",
            [(derive_display_name(b, rx, g), rid) for (rid, b, rx, g) in rows],
        )
        conn.commit()
        # Ship in rollback-journal (DELETE) mode, not WAL. A WAL database opened
        # read-only (mode=ro) on a read-only directory (Cloud Run /app, the
        # packaged Resources dir before the userData copy) fails to open. DELETE
        # mode reads cleanly from a read-only file. Checkpoint first so no WAL
        # data is lost, then drop the sidecar files.
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        journal = conn.execute("PRAGMA journal_mode=DELETE").fetchone()[0]
        conn.commit()
        after = conn.execute("SELECT COUNT(*) FROM drugs").fetchone()[0]
        populated = conn.execute(
            "SELECT COUNT(*) FROM drugs WHERE display_name IS NOT NULL AND display_name != ''"
        ).fetchone()[0]
        fts = conn.execute(
            "SELECT COUNT(*) FROM drugs_fts WHERE drugs_fts MATCH 'aspirin*'"
        ).fetchone()[0]
        sample = conn.execute(
            "SELECT generic_name, display_name FROM drugs "
            "WHERE generic_name LIKE '%AND%' LIMIT 3"
        ).fetchall()
        if before != after:
            raise SystemExit(f"FAIL: row count changed {before} -> {after} in {db_path}")
        if after != EXPECTED_ROWS:
            raise SystemExit(f"FAIL: expected {EXPECTED_ROWS} rows, found {after} in {db_path}")
        print(f"OK {db_path}: rows={after} populated={populated} journal={journal} fts_aspirin={fts}")
        for g, d in sample:
            print(f"   '{(g or '')[:48]}' -> '{d}'")
        return True
    finally:
        conn.close()
        # Remove leftover WAL sidecars so only the single .db file ships.
        for ext in ("-wal", "-shm"):
            side = Path(str(p) + ext)
            if side.exists():
                side.unlink()


def main():
    targets = sys.argv[1:] or DEFAULT_DBS
    ok_any = False
    for t in targets:
        if migrate(t):
            ok_any = True
    if not ok_any:
        raise SystemExit("FAIL: no database migrated")


if __name__ == "__main__":
    main()
