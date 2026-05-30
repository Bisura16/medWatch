"""Storage layer with auto-fallback between Cloud Storage and local disk.

When ``USE_CLOUD_STORAGE=true`` the layer reads and writes against
the configured GCS bucket. Otherwise it falls back to JSON files
under ``api/data/``. Both backends share a uniform load/save API
so route handlers never need to know which one is active.

On first read of ``users.json``, any user record that still carries
``password_plain`` is bcrypt-hashed and persisted back through the
same backend. This keeps seed data developer-friendly (plaintext
ships in the file) while guaranteeing that plaintext never lingers
beyond the first server start.
"""
import json
import logging
import os
import shutil
import tempfile
import threading
from typing import Any
from .config import DATA_DIR, SEED_DIR, USE_CLOUD_STORAGE, GCS_BUCKET
from .auth import hash_password

logger = logging.getLogger(__name__)

USERS_KEY = "users.json"
PATIENTS_KEY = "patients.json"

_gcs_client = None
# Serialises every local read-modify-write so concurrent admin/patient
# mutations cannot drop each other (last-writer-wins) on the JSON store.
_store_lock = threading.RLock()


def ensure_seeded() -> None:
    """Seed the writable data dir from the bundled seed on first launch.

    No-op when ``DATA_DIR == SEED_DIR`` (web/dev) or when the data dir
    already holds ``users.json``. In desktop mode ``DATA_DIR`` is a
    writable per-user directory that starts empty, so the bundled
    ``users.json`` / ``patients.json`` are copied in so login works and
    patient records persist across restarts.
    """
    if USE_CLOUD_STORAGE or DATA_DIR == SEED_DIR:
        return
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        for name in (USERS_KEY, PATIENTS_KEY):
            target = DATA_DIR / name
            seed = SEED_DIR / name
            if not target.exists() and seed.exists():
                shutil.copyfile(seed, target)
                logger.info("seeded %s into writable data dir", name)
    except OSError as e:
        logger.error("seeding data dir failed: %s", e)


def _gcs():
    """Lazily build the GCS client so importing this module is free.

    Imports ``google.cloud.storage`` only on first call, which keeps
    cold-start cost low in environments where Cloud Storage is not
    enabled (every local dev session).
    """
    global _gcs_client
    if _gcs_client is None:
        from google.cloud import storage as gcs
        _gcs_client = gcs.Client()
    return _gcs_client


def _load_local(filename: str) -> Any:
    """Read and JSON-parse ``DATA_DIR/filename`` or return ``None`` if absent."""
    path = DATA_DIR / filename
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_local(filename: str, data: Any) -> None:
    """Atomically write ``data`` as pretty UTF-8 JSON under ``DATA_DIR``.

    Writes to a temp file in the same directory and ``os.replace``s it
    into place so a crash mid-write can never truncate the live file.
    """
    path = DATA_DIR / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=f".{filename}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def _load_gcs(key: str) -> Any:
    """Download ``key`` from the configured GCS bucket and parse as JSON."""
    client = _gcs()
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(key)
    if not blob.exists():
        return None
    text = blob.download_as_text()
    return json.loads(text)


def _save_gcs(key: str, data: Any) -> None:
    """Upload ``data`` as JSON to ``GCS_BUCKET/key``."""
    client = _gcs()
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(key)
    blob.upload_from_string(json.dumps(data, indent=2, ensure_ascii=False),
                            content_type="application/json")


def _load(key: str, fallback_default: Any) -> Any:
    """Backend-aware loader. Seeds GCS from local on first cloud read."""
    try:
        if USE_CLOUD_STORAGE:
            data = _load_gcs(key)
            if data is None:
                # Serialise + double-check the seed so two concurrent cold
                # requests cannot both write the seed back to GCS.
                with _store_lock:
                    data = _load_gcs(key)
                    if data is not None:
                        return data
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
    """Backend-aware writer; dispatches to GCS or local disk."""
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
    """Load the full user list, hashing any plaintext passwords found.

    The read-hash-write upgrade runs under the store lock so two
    concurrent callers cannot race on persisting the hashed seed.

    Returns:
        List of user dicts. Empty list when the store is missing or
        carries a non-list root (defensive against manual edits).
    """
    with _store_lock:
        users = _load(USERS_KEY, [])
        if not isinstance(users, list):
            return []
        users, mutated = _ensure_users_hashed(users)
        if mutated:
            logger.info("plaintext passwords found; hashing and persisting")
            _save(USERS_KEY, users)
        return users


def save_users(users: list[dict]) -> None:
    """Persist the user list through the active storage backend."""
    with _store_lock:
        _save(USERS_KEY, users)


def create_user(record: dict) -> bool:
    """Atomically register a user when the username is free.

    The duplicate check, append, and save run as one critical section
    under the store lock so two concurrent registrations with the same
    username cannot both pass the check and double-write (TOCTOU).

    Returns:
        True when the user was created, False when the username is taken.
    """
    uname = (record.get("username") or "").strip().lower()
    with _store_lock:
        users = _load(USERS_KEY, [])
        if not isinstance(users, list):
            users = []
        if any((u.get("username") or "").strip().lower() == uname for u in users):
            return False
        users.append(record)
        _save(USERS_KEY, users)
    return True


def load_patients() -> list[dict]:
    """Load the full patient list.

    Returns:
        List of patient dicts in the Bimo SOAP schema. Empty list
        when the store is missing or carries a non-list root.
    """
    with _store_lock:
        patients = _load(PATIENTS_KEY, [])
        return patients if isinstance(patients, list) else []


def save_patients(patients: list[dict]) -> None:
    """Persist the patient list through the active storage backend."""
    with _store_lock:
        _save(PATIENTS_KEY, patients)


def add_patient(record: dict) -> dict:
    """Atomically append a patient record under the store lock.

    Returns the saved record so the route can echo it back.
    """
    with _store_lock:
        patients = _load(PATIENTS_KEY, [])
        if not isinstance(patients, list):
            patients = []
        patients.append(record)
        _save(PATIENTS_KEY, patients)
    return record
