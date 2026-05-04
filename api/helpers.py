"""Response helpers and shared utilities."""
from flask import jsonify


def ok(data=None, status: int = 200):
    return jsonify(data if data is not None else {"status": "ok"}), status


def err(message: str, status: int = 400, **extra):
    payload = {"error": message}
    payload.update(extra)
    return jsonify(payload), status


def strip_password_fields(user: dict) -> dict:
    """Return a copy of user with password fields removed."""
    return {k: v for k, v in user.items() if k not in ("password_hash", "password_plain", "password")}
