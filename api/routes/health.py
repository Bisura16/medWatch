"""Health and info endpoints."""
import logging
from datetime import datetime, timezone
from flask import Blueprint, jsonify
from ..config import USE_CLOUD_STORAGE, GCP_PROJECT_ID
from ..bootstrap import get_module

logger = logging.getLogger(__name__)
bp = Blueprint("health", __name__)


@bp.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "version": "1.0.0",
        "time": datetime.now(timezone.utc).isoformat(),
    })


@bp.route("/api/info", methods=["GET"])
def info():
    modules = {}
    for ang, mod in [
        ("anggota2.pasien_helper", get_module("anggota2", "pasien_helper")),
        ("anggota4.data_loader", get_module("anggota4", "data_loader")),
        ("anggota4.safety_checker", get_module("anggota4", "safety_checker")),
        ("anggota4.pencarian_obat", get_module("anggota4", "pencarian_obat")),
        ("anggota5.export_pdf", get_module("anggota5", "export_pdf")),
    ]:
        modules[ang] = mod is not None
    return jsonify({
        "modules_loaded": modules,
        "cloud_storage": USE_CLOUD_STORAGE,
        "project": GCP_PROJECT_ID,
    })
