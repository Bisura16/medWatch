"""Configuration constants for the MedWatch API.

Centralises every environment-driven knob (JWT secret, openFDA key,
CORS allowlist, port, debug flag) and every filesystem path the
backend relies on. Importing this module has no side effects beyond
reading from ``os.environ``; nothing is written to disk and no
network call is made.
"""
import os
import sys
from pathlib import Path

def _resolve_base_dir() -> Path:
    """Return the project root directory, compatible with both normal Python
    and PyInstaller frozen bundles.

    In a normal Python process the root is two levels up from ``config.py``
    (``api/config.py`` → parent ``api/`` → grandparent ``medWatch/``).
    In a PyInstaller frozen bundle the modules sit inside ``sys._MEIPASS``
    which IS the project root; the extra ``..`` does not apply because
    ``__file__`` resolves to an archive-internal path.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def _resolve_api_dir() -> Path:
    """Return the ``api/`` directory, PyInstaller-aware.

    Normal: ``config.py`` itself lives in ``api/``.
    Frozen: ``sys._MEIPASS/api/`` is the intended path.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "api"
    return Path(__file__).resolve().parent


BASE_DIR = _resolve_base_dir()
API_DIR = _resolve_api_dir()

# Seed data ships read-only inside the bundle at api/data. The desktop
# launcher points MEDWATCH_DATA_DIR at a writable per-user directory so
# patients/users persist across restarts; on first launch the seed is
# copied there. In web/dev mode both resolve to api/data (no copy).
SEED_DIR = API_DIR / "data"
_DATA_DIR_ENV = os.environ.get("MEDWATCH_DATA_DIR")
DATA_DIR = Path(_DATA_DIR_ENV).resolve() if _DATA_DIR_ENV else SEED_DIR

# When set (desktop), Flask serves the bundled Next.js static export from
# this directory as a single-page app over the loopback port. When unset
# (web/Cloud Run), Vercel serves the renderer and Flask only exposes /api.
# Resolved to an absolute path because Flask's send_from_directory treats a
# relative directory as relative to the app root, not the process cwd.
_RENDERER_DIR_ENV = os.environ.get("MEDWATCH_RENDERER_DIR")
RENDERER_DIR = Path(_RENDERER_DIR_ENV).resolve() if _RENDERER_DIR_ENV else None

ANGGOTA_DIRS = {
    "anggota1": BASE_DIR / "anggota1",
    "anggota2": BASE_DIR / "anggota2",
    "anggota3": BASE_DIR / "anggota3",
    "anggota4": BASE_DIR / "anggota4",
    "anggota5": BASE_DIR / "anggota5",
}

JWT_SECRET = os.environ.get("JWT_SECRET", "dev-only-do-not-use-in-prod")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 12

CORS_ORIGINS = [
    "https://medwatch-frontend.vercel.app",
    "http://localhost:3000",
    "http://localhost:5173",
]

GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "medwatch-polban-2026")
GCS_BUCKET = os.environ.get("GCS_BUCKET", "medwatch-polban-2026-state")
USE_CLOUD_STORAGE = os.environ.get("USE_CLOUD_STORAGE", "false").lower() == "true"

# openFDA real-data acquisition. Read from env only; the value is never
# echoed, logged, or committed. Used by anggota1/openfda/fetch.py and any
# future backend route that needs to hit api.fda.gov.
OPENFDA_API_KEY = os.environ.get("OPENFDA_API_KEY", "")

PORT = int(os.environ.get("PORT", 8080))
DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
