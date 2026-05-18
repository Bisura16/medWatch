"""Health and runtime info endpoints.

``/api/health`` is a lightweight liveness probe used by Cloud Run
and by the frontend status indicator. ``/api/info`` reports which
anggota modules loaded successfully so operators can quickly tell
whether a deployment lost any teammate dependency.
"""
import logging
from datetime import datetime, timezone
from flask import Blueprint, jsonify
from ..config import USE_CLOUD_STORAGE, GCP_PROJECT_ID
from ..bootstrap import get_module

logger = logging.getLogger(__name__)
bp = Blueprint("health", __name__)


@bp.route("/api/health", methods=["GET"])
def health():
    """Return a small status payload with the current UTC timestamp.

    Returns:
        JSON body containing ``status``, ``version``, and the server
        clock in ISO-8601 UTC. Always HTTP 200.
    """
    return jsonify({
        "status": "ok",
        "version": "1.0.0",
        "time": datetime.now(timezone.utc).isoformat(),
    })


@bp.route("/api/info", methods=["GET"])
def info():
    """Report which anggota modules loaded and the active GCP context.

    Returns:
        JSON with a ``modules_loaded`` flag map (one entry per
        anggota module the backend tries to wrap), the boolean
        ``cloud_storage`` flag, and the GCP project id.
    """
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
