"""Configuration constants for MedWatch API."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
API_DIR = Path(__file__).resolve().parent
DATA_DIR = API_DIR / "data"

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

PORT = int(os.environ.get("PORT", 8080))
DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
