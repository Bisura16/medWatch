"""Auth + role middleware decorators. Reads Authorization: Bearer header."""
import logging
from functools import wraps
from flask import request, jsonify, g
from .auth import verify_token

logger = logging.getLogger(__name__)


def _extract_token() -> str | None:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:].strip()
    return None


def require_auth(fn):
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
