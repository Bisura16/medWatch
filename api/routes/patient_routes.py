"""Patient CRUD wrapping anggota2 schema. Patient IDs use Bimo's P001 format."""
import logging
from copy import deepcopy
from flask import Blueprint, request, g, jsonify
from ..middleware import require_auth, require_role
from ..storage import load_patients, save_patients
from ..bootstrap import get_module
from ..helpers import ok, err

logger = logging.getLogger(__name__)
bp = Blueprint("patient_routes", __name__)


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
    return ok([_summary(p) for p in patients])


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
