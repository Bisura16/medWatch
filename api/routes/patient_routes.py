"""Patient CRUD endpoints wrapping the anggota2 SOAP schema.

Patient IDs follow Bimo's canonical format ``P001``, ``P002``, etc.
Numeric medical fields go through the server-side range guard that
B03 mandates so the frontend cannot be the sole line of defence.
Role-based access uses :func:`api.middleware.require_role`:
``tenaga_kesehatan`` and ``admin`` can list, create, and update;
only ``admin`` may delete a record; ``masyarakat`` may only read
their own visit via :func:`get_patient`.
"""
import logging
import re
import threading
from copy import deepcopy
from flask import Blueprint, request, g, jsonify
from ..middleware import require_auth, require_role
from ..storage import load_patients, save_patients
from ..bootstrap import get_module
from ..helpers import ok, err

logger = logging.getLogger(__name__)
bp = Blueprint("patient_routes", __name__)

# H10-1 (Wave 5): process-level lock for the read-modify-write sequence in
# POST/PUT/DELETE. Without this lock, two concurrent POSTs can both read
# the same patient list, compute the same next id, and the last writer
# wins the file rewrite. The lock is intentionally module-scoped so every
# request handled by this process serialises through it.
_patients_lock = threading.Lock()

# H01-1 (Wave 5): allowed umur range when value parses to an integer.
# Bidan input convention is either a bare integer like ``25`` or the
# bidan abbreviation ``25 THN``. Both forms must pass when the parsed
# integer falls inside (UMUR_MIN, UMUR_MAX).
UMUR_MIN = 0
UMUR_MAX = 150
_UMUR_INT_PATTERN = re.compile(r"^\s*(-?\d+)\s*(?:thn|tahun|y|yr|yrs)?\s*$", re.IGNORECASE)


# Medical field range definitions for server-side validation (B03).
# Tuple shape: (min, max, label). Composite blood pressure handled separately.
NUMERIC_RANGES: dict[str, tuple[float, float, str]] = {
    "bb_kg": (1.0, 300.0, "BB (kg)"),
    "tb_cm": (30.0, 300.0, "TB (cm)"),
    "lila_cm": (8.0, 60.0, "LILA (cm)"),
    "nadi": (30.0, 220.0, "Nadi"),
    "suhu_c": (30.0, 44.0, "Suhu (C)"),
    "respirasi": (5.0, 80.0, "Respirasi"),
}
SYSTOLIC_RANGE = (60.0, 250.0)
DIASTOLIC_RANGE = (30.0, 160.0)
TD_PATTERN = re.compile(r"^\s*(\d{1,3})\s*/\s*(\d{1,3})\s*$")


def _parse_visit_date(s: str | None) -> tuple[int, int, int]:
    """Parse DD-MM-YYYY into a (year, month, day) tuple for sorting.

    Returns (0, 0, 0) for missing/malformed dates so they sort to the bottom
    when used in a DESCENDING sort.
    """
    if not s or not isinstance(s, str):
        return (0, 0, 0)
    parts = s.strip().split("-")
    if len(parts) != 3:
        return (0, 0, 0)
    try:
        d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        return (0, 0, 0)
    return (y, m, d)


def _id_num(pid: str | None) -> int:
    """Extract numeric tail of patient id (P001 -> 1) for stable tiebreak."""
    if not pid or not isinstance(pid, str) or len(pid) < 2:
        return 0
    tail = pid[1:]
    return int(tail) if tail.isdigit() else 0


def _validate_medical_ranges(body: dict) -> list[str]:
    """Return list of human-readable error messages for any out-of-range
    or non-numeric medical fields. Empty strings and missing fields are
    treated as not-provided (allowed). All messages are Bahasa Indonesia.
    """
    errors: list[str] = []
    o = body.get("O") or {}
    if not isinstance(o, dict):
        return ["Field O harus berupa objek."]

    td_raw = (o.get("tekanan_darah") or "").strip() if isinstance(o.get("tekanan_darah"), str) else ""
    if td_raw:
        m = TD_PATTERN.match(td_raw)
        if not m:
            errors.append("Tekanan darah harus dalam format sistolik/diastolik (mis. 120/80).")
        else:
            sys_v, dia_v = float(m.group(1)), float(m.group(2))
            if not (SYSTOLIC_RANGE[0] <= sys_v <= SYSTOLIC_RANGE[1]):
                errors.append(
                    f"Tekanan darah sistolik harus antara {int(SYSTOLIC_RANGE[0])} dan {int(SYSTOLIC_RANGE[1])}."
                )
            if not (DIASTOLIC_RANGE[0] <= dia_v <= DIASTOLIC_RANGE[1]):
                errors.append(
                    f"Tekanan darah diastolik harus antara {int(DIASTOLIC_RANGE[0])} dan {int(DIASTOLIC_RANGE[1])}."
                )

    for key, (lo, hi, label) in NUMERIC_RANGES.items():
        raw = o.get(key)
        if raw is None:
            continue
        s = str(raw).strip()
        if not s:
            continue
        try:
            v = float(s.replace(",", "."))
        except ValueError:
            errors.append(f"{label} harus berupa angka.")
            continue
        if not (lo <= v <= hi):
            # Format range cleanly: floats with .0 stripped.
            lo_s = f"{lo:g}"
            hi_s = f"{hi:g}"
            errors.append(f"{label} harus antara {lo_s} dan {hi_s}.")
    return errors


def _validate_umur(body: dict) -> list[str]:
    """Validate ``umur`` accepts only sane integers in [UMUR_MIN, UMUR_MAX].

    H01-1 (Wave 5). The bidan input convention is either ``25`` or the
    abbreviated ``25 THN`` form. Empty/missing values are allowed because
    the SOAP schema marks umur as optional. Any non-empty value that is
    not parseable as an integer in range produces a Bahasa Indonesia
    field-level error.
    """
    raw = body.get("umur")
    if raw is None:
        return []
    s = str(raw).strip()
    if not s:
        return []
    m = _UMUR_INT_PATTERN.match(s)
    if not m:
        return [f"Umur harus berupa angka antara {UMUR_MIN} dan {UMUR_MAX}."]
    try:
        n = int(m.group(1))
    except ValueError:
        return [f"Umur harus berupa angka antara {UMUR_MIN} dan {UMUR_MAX}."]
    if n < UMUR_MIN or n > UMUR_MAX:
        return [f"Umur harus antara {UMUR_MIN} dan {UMUR_MAX}."]
    return []


def _generate_id(patients: list[dict]) -> str:
    """Use anggota2.pasien_helper.generate_id when available, fallback inline."""
    pasien_helper = get_module("anggota2", "pasien_helper")
    if pasien_helper and hasattr(pasien_helper, "generate_id"):
        try:
            return pasien_helper.generate_id(patients)
        except Exception as e:
            logger.warning(f"pasien_helper.generate_id failed: {e}, using fallback")
    nums = [int(p["id"][1:]) for p in patients if p.get("id", "")[1:].isdigit()]
    next_num = (max(nums) + 1) if nums else 1
    return f"P{str(next_num).zfill(3)}"


def _summary(p: dict) -> dict:
    """Return the slim patient summary projection used by the list endpoint."""
    return {
        "id": p.get("id"),
        "nama": p.get("nama"),
        "umur": p.get("umur"),
        "tanggal_kunjungan": p.get("tanggal_kunjungan"),
        "kategori": p.get("kategori"),
    }


def _deep_merge(base: dict, updates: dict) -> dict:
    """Recursively merge ``updates`` over a deep copy of ``base``.

    Nested dicts are merged key-by-key; non-dict values are
    overwritten. Used by PUT so the frontend can submit a partial
    SOAP subtree (just ``O.tekanan_darah`` for example) without
    erasing untouched sibling fields.
    """
    out = deepcopy(base)
    for k, v in updates.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


@bp.route("/api/patients", methods=["GET"])
@require_role("tenaga_kesehatan", "admin")
def list_patients():
    """List patients ordered newest visit first (fix for B07).

    Sort is descending by (parsed visit date, numeric id suffix) so
    patients with the same ``tanggal_kunjungan`` are tie-broken by
    the highest patient id.

    Returns:
        HTTP 200 with a list of slim ``_summary`` projections.
    """
    patients = load_patients()
    # B07: newest visit first. Tiebreak by descending numeric patient id so
    # P003 lists before P001 when both have the same kunjungan date.
    patients_sorted = sorted(
        patients,
        key=lambda p: (_parse_visit_date(p.get("tanggal_kunjungan")), _id_num(p.get("id"))),
        reverse=True,
    )
    return ok([_summary(p) for p in patients_sorted])


@bp.route("/api/patients/<pid>", methods=["GET"])
@require_auth
def get_patient(pid: str):
    """Return one patient record, enforcing per-role visibility.

    Args:
        pid: Patient id (for example ``P004``) from the URL.

    Returns:
        HTTP 200 with the full SOAP record. HTTP 404 when no record
        carries ``pid``. HTTP 403 when a ``masyarakat`` requests a
        record they did not create (``created_by`` mismatch).
    """
    role = g.user["role"]
    patients = load_patients()
    target = next((p for p in patients if p.get("id") == pid), None)
    if not target:
        return err("not found", 404)
    if role == "masyarakat" and target.get("created_by") != g.user["username"]:
        return err("forbidden", 403)
    return ok(target)


@bp.route("/api/patients", methods=["POST"])
@require_role("tenaga_kesehatan", "admin")
def create_patient():
    """Create a new patient SOAP record.

    Validates required fields (``nama``, ``S.keluhan``,
    ``A.diagnosa``, ``P.tindakan``) and runs the B03 numeric range
    guard. The new id is generated through
    :func:`_generate_id` so existing P-numbering stays unique.

    Returns:
        HTTP 201 with the stored record (including the assigned
        ``id``). HTTP 400 on validation failure with a ``fields``
        array detailing each broken rule.
    """
    body = request.get_json(silent=True) or {}
    if not body.get("nama"):
        return err("nama required", 400)
    if not body.get("S", {}).get("keluhan"):
        return err("S.keluhan required", 400)
    if not body.get("A", {}).get("diagnosa"):
        return err("A.diagnosa required", 400)
    if not body.get("P", {}).get("tindakan"):
        return err("P.tindakan required", 400)

    # B03 + H01-1: server-side range validation for numeric medical
    # fields plus umur.
    umur_errs = _validate_umur(body)
    medical_errs = _validate_medical_ranges(body)
    all_errs = umur_errs + medical_errs
    if all_errs:
        return err("Validasi gagal", 400, fields=all_errs)

    # H10-1: serialise the read-modify-write block so two concurrent
    # POSTs cannot allocate the same id or drop each other's records.
    with _patients_lock:
        patients = load_patients()
        new_patient = deepcopy(body)
        new_patient["id"] = _generate_id(patients)
        new_patient["created_by"] = g.user["username"]
        patients.append(new_patient)
        save_patients(patients)
    logger.info(f"patient created: {new_patient['id']} by {g.user['username']}")
    return ok(new_patient, status=201)


@bp.route("/api/patients/<pid>", methods=["PUT"])
@require_role("tenaga_kesehatan", "admin")
def update_patient(pid: str):
    """Apply a partial deep-merge update to an existing record.

    The B03 numeric range guard runs again on edits so an admin
    cannot inject nonsense values through the JSON API.

    Args:
        pid: Patient id from the URL.

    Returns:
        HTTP 200 with the merged record. HTTP 404 when no patient
        matches ``pid``. HTTP 400 when validation fails.
    """
    body = request.get_json(silent=True) or {}
    # B03 + H01-1: server-side range validation for numeric medical
    # fields plus umur on edit.
    umur_errs = _validate_umur(body)
    medical_errs = _validate_medical_ranges(body)
    all_errs = umur_errs + medical_errs
    if all_errs:
        return err("Validasi gagal", 400, fields=all_errs)
    # H10-1: same lock as create_patient so PUT cannot stomp a concurrent
    # POST mid-write.
    with _patients_lock:
        patients = load_patients()
        for i, p in enumerate(patients):
            if p.get("id") == pid:
                patients[i] = _deep_merge(p, body)
                patients[i]["id"] = pid
                save_patients(patients)
                return ok(patients[i])
    return err("not found", 404)


@bp.route("/api/patients/<pid>", methods=["DELETE"])
@require_role("admin")
def delete_patient(pid: str):
    """Delete a patient record. Admin-only.

    Args:
        pid: Patient id from the URL.

    Returns:
        HTTP 204 (empty body) on success. HTTP 404 when no record
        matches ``pid``.
    """
    # H10-1: serialise delete with the same lock to avoid losing a
    # concurrent POST that the caller did not yet see.
    with _patients_lock:
        patients = load_patients()
        new_patients = [p for p in patients if p.get("id") != pid]
        if len(new_patients) == len(patients):
            return err("not found", 404)
        save_patients(new_patients)
    logger.info(f"patient deleted: {pid} by {g.user['username']}")
    return ("", 204)
