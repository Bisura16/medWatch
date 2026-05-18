"""Authentication endpoints (login, me, logout).

Every login attempt returns a generic ``invalid credentials`` error
regardless of whether the username, the password, or both were
wrong, to prevent user-enumeration probing. Successful logins
return a signed JWT plus the stripped user record.
"""
import logging
from flask import Blueprint, request, g, jsonify
from ..auth import verify_password, issue_token
from ..middleware import require_auth
from ..storage import load_users
from ..helpers import ok, err

logger = logging.getLogger(__name__)
bp = Blueprint("auth_routes", __name__)


@bp.route("/api/auth/login", methods=["POST"])
def login():
    """Verify credentials and issue a JWT.

    Request body: ``{username, password}``.

    Returns:
        HTTP 200 with ``{token, user}`` on success.
        HTTP 401 with ``{error: "invalid credentials"}`` for any
        failure mode (missing field, unknown user, bad password).
    """
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return err("invalid credentials", 401)

    users = load_users()
    for u in users:
        if u.get("username") == username:
            if verify_password(password, u.get("password_hash", "")):
                token = issue_token(u["username"], u["role"], u.get("name", ""))
                logger.info(f"login ok: {username} as {u['role']}")
                return ok({
                    "token": token,
                    "user": {
                        "username": u["username"],
                        "role": u["role"],
                        "name": u.get("name", ""),
                    },
                })
            logger.warning(f"login bad password: {username}")
            return err("invalid credentials", 401)

    logger.warning(f"login user not found: {username}")
    return err("invalid credentials", 401)


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
