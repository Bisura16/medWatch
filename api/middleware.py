"""Authentication and role-gating decorators for Flask routes.

Reads the ``Authorization: Bearer <jwt>`` header, validates the
token via :func:`api.auth.verify_token`, and exposes the decoded
identity at ``flask.g.user``. ``require_role`` composes on top of
``require_auth`` so the two cannot be applied independently in the
wrong order.
"""
import logging
from functools import wraps
from flask import request, jsonify, g
from .auth import verify_token

logger = logging.getLogger(__name__)


def _extract_token() -> str | None:
    """Pull the bearer token out of the ``Authorization`` header.

    Returns ``None`` when the header is absent or does not start
    with the literal ``Bearer `` prefix.
    """
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:].strip()
    return None


def require_auth(fn):
    """Decorator that rejects unauthenticated requests with HTTP 401.

    On success the decoded JWT payload is exposed as
    ``flask.g.user`` with keys ``username``, ``role``, and ``name``
    so downstream handlers do not need to re-decode the token.

    Args:
        fn: Flask view function to wrap.

    Returns:
        Wrapped view function that short-circuits with HTTP 401
        whenever the token is missing, malformed, expired, or
        signed with the wrong key.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = _extract_token()
        if not token:
            logger.warning(f"auth missing on {request.path}")
            return jsonify({"error": "missing or invalid token"}), 401
        payload = verify_token(token)
        if not payload:
            logger.warning(f"auth invalid on {request.path}")
            return jsonify({"error": "missing or invalid token"}), 401
        g.user = {
            "username": payload["sub"],
            "role": payload["role"],
            "name": payload.get("name", ""),
        }
        return fn(*args, **kwargs)
    return wrapper


def require_role(*allowed_roles):
    """Decorator factory that gates a route to a fixed set of roles.

    Internally stacks on top of :func:`require_auth`, so a missing
    token still produces HTTP 401 while a wrong role produces
    HTTP 403. Either denial is logged with the offending username
    and the required role list for audit purposes.

    Args:
        *allowed_roles: One or more role strings drawn from
            ``tenaga_kesehatan``, ``masyarakat``, ``admin``.

    Returns:
        Decorator that wraps the target Flask view function.
    """
    def decorator(fn):
        @wraps(fn)
        @require_auth
        def wrapper(*args, **kwargs):
            user_role = g.user.get("role")
            if user_role not in allowed_roles:
                logger.warning(
                    f"role denied on {request.path}: user={g.user['username']} "
                    f"role={user_role} required={allowed_roles}"
                )
                return jsonify({"error": "forbidden"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
