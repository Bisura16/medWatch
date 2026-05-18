"""Visualization endpoints. Returns Recharts-friendly JSON.

anggota3 BacaData.py has a known SyntaxError so we cannot import it.
This module implements equivalent data extraction inline from
api/data/patients.json + anggota4/data/drug_database.json + effect_database.json.
"""
import logging
from collections import Counter, defaultdict
from flask import Blueprint
from ..middleware import require_auth, require_role
from ..bootstrap import get_module
from ..storage import load_patients
from ..helpers import ok

logger = logging.getLogger(__name__)
bp = Blueprint("visualization_routes", __name__)

NAMA_BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
              "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]


def _parse_month(tanggal_str: str) -> int | None:
    """Parse DD-MM-YYYY -> month index 0-11."""
    if not tanggal_str:
        return None
    parts = tanggal_str.split("-")
    if len(parts) < 2:
        return None
    try:
        m = int(parts[1])
        if 1 <= m <= 12:
            return m - 1
    except ValueError:
        pass
    return None


def _dummy_kunjungan_trend() -> list[dict]:
    """Fallback trend data when patient set is empty."""
    sample = [12, 18, 25, 22, 30, 28, 35, 40, 38, 42, 48, 52]
    return [{"month": NAMA_BULAN[i], "count": sample[i]} for i in range(12)]


def _dummy_keluhan_distribution() -> list[dict]:
    return [
        {"kategori": "Ibu Hamil", "count": 28},
        {"kategori": "KB", "count": 22},
        {"kategori": "Anak", "count": 18},
        {"kategori": "Imunisasi", "count": 15},
        {"kategori": "Umum", "count": 32},
    ]


@bp.route("/api/visualizations/kunjungan-trend", methods=["GET"])
@require_role("tenaga_kesehatan", "admin")
def kunjungan_trend():
    """Twelve-month patient visit trend.

    Returns:
        HTTP 200 with a 12-element list of ``{month, count}``.
        Falls back to a sample series when the patient store is
        empty so the chart never renders as a flat line.
    """
    patients = load_patients()
    if not patients:
        return ok(_dummy_kunjungan_trend())

    counts = [0] * 12
    for p in patients:
        idx = _parse_month(p.get("tanggal_kunjungan", ""))
        if idx is not None:
            counts[idx] += 1
    return ok([{"month": NAMA_BULAN[i], "count": counts[i]} for i in range(12)])


@bp.route("/api/visualizations/keluhan-distribution", methods=["GET"])
@require_role("tenaga_kesehatan", "admin")
def keluhan_distribution():
    """Patient distribution per ``kategori`` (Ibu Hamil, KB, ...).

    Returns:
        HTTP 200 with a list of ``{kategori, count}`` ordered by
        descending count. Falls back to a sample distribution when
        the patient store is empty.
    """
    patients = load_patients()
    if not patients:
        return ok(_dummy_keluhan_distribution())

    by_kategori = Counter(p.get("kategori", "Umum") or "Umum" for p in patients)
    return ok([
        {"kategori": k, "count": v}
        for k, v in sorted(by_kategori.items(), key=lambda x: -x[1])
    ])


@bp.route("/api/visualizations/top-efek-samping", methods=["GET"])
@require_auth
def top_efek_samping():
    """Compute top-10 side effects from drug_database.json + effect_database.json.
    Each side effect's frequency = count of drugs that list it."""
    dl = get_module("anggota4", "data_loader")
    if not dl:
        return ok([])

    drugs = dl.muat_database_obat()
    effect_index = dl.buat_index_efek_samping()

    counter: Counter[str] = Counter()
    for d in drugs:
        for e in d.get("efek_samping", []):
            key = dl.normalisasi_teks(e)
            counter[key] += 1

    out = []
    for nama_norm, count in counter.most_common(10):
        info = effect_index.get(nama_norm, {})
        out.append({
            "nama_efek": info.get("nama_efek", nama_norm.title()),
            "count": count,
            "kategori": info.get("kategori", "Lain-lain"),
            "tingkat_keparahan": info.get("tingkat_keparahan", "ringan"),
        })
    return ok(out)


@bp.route("/api/visualizations/heatmap-efek", methods=["GET"])
@require_auth
def heatmap_efek():
    """Drug x effect matrix, values are 1 (effect present) or 0 (absent)."""
    dl = get_module("anggota4", "data_loader")
    if not dl:
        return ok({"drugs": [], "effects": [], "values": []})

    drugs = dl.muat_database_obat()
    all_effects: set[str] = set()
    for d in drugs:
        all_effects.update(d.get("efek_samping", []))

    drug_names = [d.get("nama_obat", "?") for d in drugs]
    effect_list = sorted(all_effects)
    values = []
    for d in drugs:
        d_effects = set(d.get("efek_samping", []))
        row = [1 if e in d_effects else 0 for e in effect_list]
        values.append(row)

    return ok({
        "drugs": drug_names,
        "effects": effect_list,
        "values": values,
    })
