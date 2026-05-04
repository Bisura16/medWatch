"""Storage layer with auto-fallback: Cloud Storage when USE_CLOUD_STORAGE=true,
local file under api/data/ otherwise.

On first read of users.json, plaintext password fields are bcrypt-hashed and
the file is rewritten back. This means seed data ships with plaintext
(developer convenience) but never persists plaintext after first server start.
"""
import json
import logging
from typing import Any
from .config import DATA_DIR, USE_CLOUD_STORAGE, GCS_BUCKET
from .auth import hash_password

logger = logging.getLogger(__name__)

USERS_KEY = "users.json"
PATIENTS_KEY = "patients.json"

_gcs_client = None


def _gcs():
    global _gcs_client
    if _gcs_client is None:
        from google.cloud import storage as gcs
        _gcs_client = gcs.Client()
    return _gcs_client


def _load_local(filename: str) -> Any:
    path = DATA_DIR / filename
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_local(filename: str, data: Any) -> None:
    path = DATA_DIR / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _load_gcs(key: str) -> Any:
    client = _gcs()
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(key)
    if not blob.exists():
        return None
    text = blob.download_as_text()
    return json.loads(text)


def _save_gcs(key: str, data: Any) -> None:
    client = _gcs()
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(key)
    blob.upload_from_string(json.dumps(data, indent=2, ensure_ascii=False),
                            content_type="application/json")


def _load(key: str, fallback_default: Any) -> Any:
    try:
        if USE_CLOUD_STORAGE:
            data = _load_gcs(key)
            if data is None:
                logger.info(f"GCS {key} missing, seeding from local fallback")
                local = _load_local(key)
                if local is not None:
                    _save_gcs(key, local)
                    return local
                return fallback_default
            return data
        else:
            data = _load_local(key)
            return data if data is not None else fallback_default
    except Exception as e:
        logger.error(f"load {key} failed: {e}, returning fallback")
        return fallback_default


def _save(key: str, data: Any) -> None:
    if USE_CLOUD_STORAGE:
        _save_gcs(key, data)
    else:
        _save_local(key, data)


def _ensure_users_hashed(users: list[dict]) -> tuple[list[dict], bool]:
    """If any user has password_plain (no password_hash), hash it.
    Returns (users, mutated_flag)."""
    mutated = False
    for u in users:
        if "password_plain" in u and "password_hash" not in u:
            u["password_hash"] = hash_password(u.pop("password_plain"))
            mutated = True
    return users, mutated


def load_users() -> list[dict]:
    users = _load(USERS_KEY, [])
    if not isinstance(users, list):
        return []
    users, mutated = _ensure_users_hashed(users)
    if mutated:
        logger.info("plaintext passwords found; hashing and persisting")
        _save(USERS_KEY, users)
    return users


def save_users(users: list[dict]) -> None:
    _save(USERS_KEY, users)


def load_patients() -> list[dict]:
    patients = _load(PATIENTS_KEY, [])
    return patients if isinstance(patients, list) else []


def save_patients(patients: list[dict]) -> None:
    _save(PATIENTS_KEY, patients)
