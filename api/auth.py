"""Auth primitives: bcrypt password hashing, JWT issuance, JWT verification.

No Flask dependencies; unit-testable in isolation. The JWT secret,
algorithm, and expiry are read from ``api.config`` so the same
helpers work in local dev (env-provided secret) and on Cloud Run
(Secret Manager-provided secret).
"""
import bcrypt
import jwt
from datetime import datetime, timezone, timedelta
from .config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRY_HOURS


def hash_password(plain: str) -> str:
    """Return a bcrypt hash for ``plain`` using cost factor 12.

    Args:
        plain: Plaintext password supplied by the user.

    Returns:
        bcrypt hash encoded as UTF-8 string suitable for JSON storage.
    """
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Constant-time bcrypt verification with a defensive guard.

    Args:
        plain: Plaintext password from the login form.
        hashed: Stored bcrypt hash to compare against.

    Returns:
        ``True`` when the password matches the hash. Any bcrypt
        error (malformed hash, encoding error) yields ``False`` so a
        broken stored record cannot trigger a 500.
    """
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def issue_token(username: str, role: str, name: str) -> str:
    """Issue a signed JWT for a successful login.

    Args:
        username: Subject identifier; copied to the ``sub`` claim.
        role: One of ``tenaga_kesehatan``, ``masyarakat``, ``admin``.
        name: Display name copied into the token for the frontend.

    Returns:
        Encoded JWT string. ``iat``/``exp`` are UTC Unix timestamps;
        ``exp`` is ``JWT_EXPIRY_HOURS`` ahead of ``iat``. Issuer is
        the fixed string ``medwatch-api``.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "role": role,
        "name": name,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=JWT_EXPIRY_HOURS)).timestamp()),
        "iss": "medwatch-api",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict | None:
    """Decode and validate a JWT.

    Args:
        token: Encoded JWT, typically taken from the
            ``Authorization: Bearer ...`` header.

    Returns:
        Decoded payload dict on success, or ``None`` when the token
        is expired, malformed, signed with the wrong key, or carries
        the wrong issuer claim.
    """
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], issuer="medwatch-api")
    except jwt.PyJWTError:
        return None
