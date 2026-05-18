"""Patient CRUD wrapping anggota2 schema. Patient IDs use Bimo's P001 format."""
import logging
import re
from copy import deepcopy
from flask import Blueprint, request, g, jsonify
from ..middleware import require_auth, require_role
from ..storage import load_patients, save_patients
from ..bootstrap import get_module
from ..helpers import ok, err

logger = logging.getLogger(__name__)
bp = Blueprint("patient_routes", __name__)


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
    return {
        "id": p.get("id"),
        "nama": p.get("nama"),
        "umur": p.get("umur"),
        "tanggal_kunjungan": p.get("tanggal_kunjungan"),
        "kategori": p.get("kategori"),
    }


def _deep_merge(base: dict, updates: dict) -> dict:
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
    role = g.user["role"]
    patients = load_patients()
    target = next((p for p in patients if p.get("id") == pid), None)
    if not target:
        return err("not found", 404)
    if role == "masyarakat" and target.get("owner_username") != g.user["username"]:
        return err("forbidden", 403)
    return ok(target)


@bp.route("/api/patients", methods=["POST"])
@require_role("tenaga_kesehatan", "admin")
def create_patient():
    body = request.get_json(silent=True) or {}
    if not body.get("nama"):
        return err("nama required", 400)
    if not body.get("S", {}).get("keluhan"):
        return err("S.keluhan required", 400)
    if not body.get("A", {}).get("diagnosa"):
        return err("A.diagnosa required", 400)
    if not body.get("P", {}).get("tindakan"):
        return err("P.tindakan required", 400)

    # B03: server-side range validation for numeric medical fields.
    medical_errs = _validate_medical_ranges(body)
    if medical_errs:
        return err("Validasi gagal", 400, fields=medical_errs)

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
    body = request.get_json(silent=True) or {}
    # B03: server-side range validation for numeric medical fields on edit.
    medical_errs = _validate_medical_ranges(body)
    if medical_errs:
        return err("Validasi gagal", 400, fields=medical_errs)
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
    patients = load_patients()
    new_patients = [p for p in patients if p.get("id") != pid]
    if len(new_patients) == len(patients):
        return err("not found", 404)
    save_patients(new_patients)
    logger.info(f"patient deleted: {pid} by {g.user['username']}")
    return ("", 204)
