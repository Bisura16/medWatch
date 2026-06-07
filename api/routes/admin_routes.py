"""Admin-only endpoints: scraper trigger, user CRUD, system stats.

Every route in this blueprint is gated by
``@require_role("admin")``. The scraper endpoint is intentionally
mocked: the real Selenium crawl in ``anggota1`` is preserved so it
can still be run manually, but invoking it inline from a request
handler would block a Cloud Run worker for minutes. The dashboard
KPIs (B10) read from real storage rather than hardcoded values.
"""
import logging
import time
from datetime import datetime, timezone
from flask import Blueprint, request, g
from ..middleware import require_role
from ..auth import hash_password
from ..security import validate_password
from ..storage import load_users, save_users, load_patients
from ..bootstrap import get_module
from ..helpers import ok, err, strip_password_fields

logger = logging.getLogger(__name__)
bp = Blueprint("admin_routes", __name__)

_LAST_SCRAPE: dict = {}
# Process start time captured once at module import. Used to compute real
# backend uptime for the admin dashboard KPI (B10).
_PROCESS_STARTED_AT = datetime.now(timezone.utc)


@bp.route("/api/admin/scrape", methods=["POST"])
@require_role("admin")
def trigger_scrape():
    """Mocked scraper trigger that simulates a 3-second crawl.

    The real Selenium-style crawl in anggota1 stays runnable
    manually. Production wiring would invoke anggota1 in a worker
    queue rather than inline.

    Returns:
        HTTP 200 with the synthetic scrape summary.
    """
    logger.info(f"scraper triggered by {g.user['username']}")
    time.sleep(3)
    dl = get_module("anggota4", "data_loader")
    drugs_count = len(dl.muat_database_obat()) if dl else 0
    result = {
        "status": "completed",
        "drugs_updated": drugs_count,
        "recalls_added": 0,
        "source": "cached",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    _LAST_SCRAPE.update(result)
    return ok(result)


@bp.route("/api/admin/users", methods=["GET"])
@require_role("admin")
def list_users():
    """List every user with password fields stripped.

    Returns:
        HTTP 200 with a list of user dicts. Stripping is enforced
        via :func:`api.helpers.strip_password_fields` so no hash
        leaks even if a new password-like key is introduced later.
    """
    users = load_users()
    return ok([strip_password_fields(u) for u in users])


@bp.route("/api/admin/users", methods=["POST"])
@require_role("admin")
def create_user():
    """Create a user with a bcrypt-hashed password.

    Request body: ``{username?, password, role, name?, phone?}``.
    When ``username`` is omitted, it is derived from
    ``name.lower().replace(" ", "")`` plus the last 4 digits of
    ``phone`` so the bidan does not need to invent a handle.

    Returns:
        HTTP 201 with the stripped record. HTTP 400 when a required
        field is missing or ``role`` is invalid. HTTP 409 when the
        username is already taken.
    """
    body = request.get_json(silent=True) or {}
    username = (body.get("username") or "").strip()
    password = body.get("password") or ""
    role = body.get("role") or ""
    name = body.get("name") or ""
    phone = body.get("phone") or ""

    if not username:
        if name and phone:
            base = name.lower().replace(" ", "")
            username = f"{base}{phone[-4:]}"
        else:
            return err("username or (name + phone) required", 400)

    if not password:
        return err("password required", 400)

    if role not in ("tenaga_kesehatan", "masyarakat", "admin"):
        return err("invalid role", 400)

    # Enforce the same password policy as self-registration so an admin
    # account (the highest privilege) can never be created with a trivial
    # password. Previously this route skipped the policy entirely.
    valid, reason = validate_password(password, username)
    if not valid:
        return err(reason, 400)

    users = load_users()
    if any((u.get("username") or "").lower() == username.lower() for u in users):
        return err("username exists", 409)

    new_user = {
        "username": username,
        "password_hash": hash_password(password),
        "role": role,
        "name": name,
        "phone": phone,
    }
    users.append(new_user)
    save_users(users)
    logger.info(f"user created: {username} as {role} by {g.user['username']}")
    return ok(strip_password_fields(new_user), status=201)


@bp.route("/api/admin/users/<username>", methods=["DELETE"])
@require_role("admin")
def delete_user(username: str):
    """Delete a user, refusing to remove the last remaining admin.

    Args:
        username: User to remove (from URL path).

    Returns:
        HTTP 204 on success. HTTP 404 when no user matches. HTTP 400
        when the target is the only admin (lockout prevention).
    """
    users = load_users()

    admin_count = sum(1 for u in users if u.get("role") == "admin")
    target = next((u for u in users if u.get("username") == username), None)
    if not target:
        return err("not found", 404)
    if target.get("role") == "admin" and admin_count <= 1:
        return err("cannot delete last admin", 400)

    new_users = [u for u in users if u.get("username") != username]
    save_users(new_users)
    logger.info(f"user deleted: {username} by {g.user['username']}")
    return ("", 204)


@bp.route("/api/admin/system-stats", methods=["GET"])
@require_role("admin")
def system_stats():
    """Report real-time system KPIs for the admin dashboard (B10 fix).

    Returns:
        HTTP 200 with counts (users, patients, drugs), the role
        breakdown, the last mocked scrape summary, and the process
        start time plus uptime in seconds. Values are computed live
        from storage and from the process so the dashboard never
        shows stale or hardcoded numbers.
    """
    users = load_users()
    patients = load_patients()
    dl = get_module("anggota4", "data_loader")
    drugs_count = len(dl.muat_database_obat()) if dl else 0
    now = datetime.now(timezone.utc)
    uptime_seconds = int((now - _PROCESS_STARTED_AT).total_seconds())
    return ok({
        "users_count": len(users),
        "patients_count": len(patients),
        "drugs_count": drugs_count,
        "last_scrape": _LAST_SCRAPE if _LAST_SCRAPE else None,
        "users_by_role": {
            "tenaga_kesehatan": sum(1 for u in users if u.get("role") == "tenaga_kesehatan"),
            "masyarakat": sum(1 for u in users if u.get("role") == "masyarakat"),
            "admin": sum(1 for u in users if u.get("role") == "admin"),
        },
        "process_started_at": _PROCESS_STARTED_AT.isoformat(),
        "uptime_seconds": uptime_seconds,
    })
