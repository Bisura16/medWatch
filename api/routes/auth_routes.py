"""Authentication endpoints (login, register, me, logout).

Every login attempt returns a generic ``invalid credentials`` error
regardless of which field was wrong, to prevent user-enumeration, and
runs a dummy hash on the unknown-user path so response timing does not
leak account existence. Failed attempts are rate limited with lockout.
Self-service registration is scoped to the public roles only; the
admin role can never be self-registered.
"""
import logging
from flask import Blueprint, request, g

from ..auth import (
    verify_password,
    issue_token,
    hash_password,
    needs_rehash,
    verify_dummy,
)
from ..middleware import require_auth
from ..storage import load_users, save_users, create_user
from ..security import validate_password
from .. import ratelimit
from ..helpers import ok, err

logger = logging.getLogger(__name__)
bp = Blueprint("auth_routes", __name__)

_PUBLIC_ROLES = ("tenaga_kesehatan", "masyarakat")


def _client_ip() -> str:
    """Return the request client IP for rate-limit keying."""
    return request.remote_addr or "unknown"


@bp.route("/api/auth/login", methods=["POST"])
def login():
    """Verify credentials and issue a JWT.

    Request body: ``{username, password}``.

    Returns:
        HTTP 200 with ``{token, user}`` on success.
        HTTP 401 with ``{error: "invalid credentials"}`` for any
        failure. HTTP 429 when the username/IP pair is locked out.
    """
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    rl_key = f"login:{username.lower()}:{_client_ip()}"
    locked, retry_after = ratelimit.check(rl_key)
    if locked:
        return err(
            "too many attempts, try again later", 429, retry_after=retry_after
        )

    if not username or not password:
        ratelimit.record_failure(rl_key)
        return err("invalid credentials", 401)

    users = load_users()
    uname_lc = username.lower()
    record = next((u for u in users if (u.get("username") or "").lower() == uname_lc), None)

    if record is None:
        verify_dummy()  # equalise timing for unknown users
        ratelimit.record_failure(rl_key)
        logger.warning("login user not found")
        return err("invalid credentials", 401)

    stored = record.get("password_hash", "")
    if not verify_password(password, stored):
        ratelimit.record_failure(rl_key)
        logger.warning("login bad password for %s", username)
        return err("invalid credentials", 401)

    # Transparently upgrade legacy bcrypt / outdated hashes to Argon2id.
    if needs_rehash(stored):
        try:
            record["password_hash"] = hash_password(password)
            save_users(users)
            logger.info("upgraded password hash for %s", username)
        except Exception as e:
            logger.warning("hash upgrade failed for %s: %s", username, e)

    ratelimit.reset(rl_key)
    token = issue_token(record["username"], record["role"], record.get("name", ""))
    logger.info("login ok: %s as %s", username, record["role"])
    return ok({
        "token": token,
        "user": {
            "username": record["username"],
            "role": record["role"],
            "name": record.get("name", ""),
        },
    })


_DEMO_ADMIN_USERNAME = "admin_ghaisan"


@bp.route("/api/auth/demo-admin", methods=["POST"])
def demo_admin():
    """Issue a token for the seeded admin demo account (web showcase tour).

    The web entry screen offers a one-click admin tour. Rather than ship the
    admin password in the static bundle, the client calls this passwordless
    endpoint and the server mints a token for the pre-seeded demo admin only.
    Arbitrary usernames are never accepted; it is lightly rate limited per IP.

    Returns:
        HTTP 200 with ``{token, user}`` when the seeded demo admin exists,
        HTTP 404 when it does not, HTTP 429 when rate limited.
    """
    rl_key = f"demo-admin:{_client_ip()}"
    locked, retry_after = ratelimit.check(rl_key)
    if locked:
        return err("too many attempts, try again later", 429, retry_after=retry_after)

    record = next(
        (u for u in load_users()
         if (u.get("username") or "").lower() == _DEMO_ADMIN_USERNAME
         and u.get("role") == "admin"),
        None,
    )
    if record is None:
        ratelimit.record_failure(rl_key)
        return err("demo admin tidak tersedia", 404)

    token = issue_token(record["username"], record["role"], record.get("name", ""))
    logger.info("demo admin tour token issued")
    return ok({
        "token": token,
        "user": {
            "username": record["username"],
            "role": record["role"],
            "name": record.get("name", ""),
        },
    })


@bp.route("/api/auth/register", methods=["POST"])
def register():
    """Self-service registration for the public roles.

    Request body: ``{username, password, name, role, phone?}``.
    ``role`` must be ``tenaga_kesehatan`` or ``masyarakat``; ``admin``
    is rejected. The password policy is enforced here regardless of any
    client-side strength meter.

    Returns:
        HTTP 201 with ``{token, user}`` (auto-login) on success.
        HTTP 400 on validation failure, HTTP 409 when the username is
        taken, HTTP 429 when registration is rate limited.
    """
    rl_key = f"register:{_client_ip()}"
    locked, retry_after = ratelimit.check(rl_key)
    if locked:
        return err("too many attempts, try again later", 429, retry_after=retry_after)

    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    name = (data.get("name") or "").strip()
    phone = (data.get("phone") or "").strip()
    role = (data.get("role") or "").strip()

    if role not in _PUBLIC_ROLES:
        return err("invalid role", 400)
    if not username or len(username) < 3 or len(username) > 32:
        return err("username harus 3 sampai 32 karakter", 400)
    if not username.replace("_", "").isalnum():
        return err("username hanya boleh huruf, angka, dan garis bawah", 400)
    if not name:
        return err("nama wajib diisi", 400)

    valid, reason = validate_password(password, username)
    if not valid:
        ratelimit.record_failure(rl_key)
        return err(reason, 400)

    record = {
        "username": username,
        "password_hash": hash_password(password),
        "role": role,
        "name": name,
        "phone": phone,
    }
    if not create_user(record):
        return err("username sudah terdaftar", 409)
    # Successful registration clears the failure counter, mirroring login.
    ratelimit.reset(rl_key)
    logger.info("registered new user %s as %s", username, role)

    token = issue_token(username, role, name)
    return ok({
        "token": token,
        "user": {"username": username, "role": role, "name": name},
    }, 201)


@bp.route("/api/auth/me", methods=["GET"])
@require_auth
def me():
    """Return the decoded identity attached to the current bearer token.

    Returns:
        HTTP 200 with ``{username, role, name}``. HTTP 401 when the
        token is missing or invalid (enforced by ``require_auth``).
    """
    return ok(g.user)


@bp.route("/api/auth/logout", methods=["POST"])
def logout():
    """Acknowledge logout. JWTs are stateless, so the server has no session
    to invalidate; the client is expected to drop its token.

    Returns:
        HTTP 200 with ``{status: "logged_out"}``.
    """
    return ok({"status": "logged_out"})
