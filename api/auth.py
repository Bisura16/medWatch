"""Auth primitives: Argon2id password hashing, JWT issuance and verification.

Passwords are hashed with Argon2id (OWASP-recommended parameters) and
an optional server-side pepper. Legacy bcrypt hashes are still
verified so existing seed accounts keep working and are transparently
upgraded to Argon2id on the next successful login.

The JWT signing secret is resolved once at first use: an explicit
strong ``JWT_SECRET`` from the environment takes precedence; otherwise
a random per-install secret is generated and persisted under the
writable data directory, so the bundled offline backend never signs
tokens with a public default key.

No Flask dependencies; unit-testable in isolation.
"""
import hmac
import logging
import os
import secrets
from datetime import datetime, timezone, timedelta

import bcrypt
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from .config import JWT_ALGORITHM, JWT_EXPIRY_HOURS, JWT_SECRET, DATA_DIR

logger = logging.getLogger(__name__)

# Argon2id parameters within the OWASP-recommended range (19 MiB memory,
# 2 iterations, 1 lane) - strong while keeping desktop login responsive.
_ph = PasswordHasher(time_cost=2, memory_cost=19456, parallelism=1, hash_len=32, salt_len=16)

# Optional server-side pepper. Appended to the password before hashing so
# a stolen database alone cannot be brute-forced without it. On the bundled
# offline desktop the pepper ships with the app (documented trade-off).
_PEPPER = os.environ.get("MEDWATCH_PEPPER", "")

# Pre-computed Argon2id hash of a fixed string, verified on the unknown-user
# login path so response timing does not reveal whether a username exists.
_DUMMY_HASH = _ph.hash("medwatch-dummy-password-for-constant-time")


def _peppered(plain: str) -> bytes:
    """Return the password combined with the pepper, UTF-8 encoded."""
    return (plain + _PEPPER).encode("utf-8")


def hash_password(plain: str) -> str:
    """Return an Argon2id hash for ``plain`` (with pepper applied)."""
    return _ph.hash(_peppered(plain))


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against an Argon2id or legacy bcrypt hash.

    Args:
        plain: Plaintext password from the login form.
        hashed: Stored hash, either Argon2id (``$argon2...``) or a
            legacy bcrypt hash (``$2...``).

    Returns:
        ``True`` when the password matches. Any malformed-hash or
        decoding error yields ``False`` so a broken record cannot
        trigger a 500.
    """
    if not hashed:
        return False
    try:
        if hashed.startswith("$argon2"):
            return _ph.verify(hashed, _peppered(plain))
        if hashed.startswith("$2"):
            # Legacy bcrypt (cost 12). bcrypt silently truncates at 72 bytes;
            # peppered input keeps the same behaviour as the original seed.
            return bcrypt.checkpw(_peppered(plain), hashed.encode("utf-8"))
        return False
    except (VerifyMismatchError, InvalidHashError, ValueError):
        return False
    except Exception:
        return False


def needs_rehash(hashed: str) -> bool:
    """Return ``True`` when a stored hash should be upgraded to current params.

    Legacy bcrypt hashes and Argon2id hashes with outdated parameters
    both report ``True`` so the caller can re-hash on next login.
    """
    if not hashed or not hashed.startswith("$argon2"):
        return True
    try:
        return _ph.check_needs_rehash(hashed)
    except InvalidHashError:
        return True


def verify_dummy() -> None:
    """Run a verify against a fixed dummy hash to equalise login timing."""
    try:
        _ph.verify(_DUMMY_HASH, b"wrong-password")
    except VerifyMismatchError:
        pass
    except Exception:
        pass


_jwt_secret: str | None = None


def _secret() -> str:
    """Resolve and cache the JWT signing secret.

    Order: a strong (>=32 char) ``JWT_SECRET`` from the environment,
    otherwise a random per-install secret persisted under the data
    directory. Never returns the weak development placeholder.
    """
    global _jwt_secret
    if _jwt_secret is not None:
        return _jwt_secret
    env = JWT_SECRET
    if env and env != "dev-only-do-not-use-in-prod" and len(env) >= 32:
        _jwt_secret = env
        return _jwt_secret
    secret_path = DATA_DIR / ".jwt_secret"
    try:
        if secret_path.exists():
            value = secret_path.read_text(encoding="utf-8").strip()
            if len(value) >= 32:
                _jwt_secret = value
                return _jwt_secret
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        value = secrets.token_hex(32)
        secret_path.write_text(value, encoding="utf-8")
        try:
            os.chmod(secret_path, 0o600)
        except OSError:
            pass
        _jwt_secret = value
        logger.info("generated a per-install JWT secret")
        return _jwt_secret
    except OSError:
        # Last resort: a process-lifetime random secret (tokens won't
        # survive a restart, but they are never forgeable with a public key).
        _jwt_secret = secrets.token_hex(32)
        return _jwt_secret


def issue_token(username: str, role: str, name: str) -> str:
    """Issue a signed JWT for a successful login.

    Args:
        username: Subject identifier; copied to the ``sub`` claim.
        role: One of ``tenaga_kesehatan``, ``masyarakat``, ``admin``.
        name: Display name copied into the token for the frontend.

    Returns:
        Encoded JWT string. ``iat``/``exp`` are UTC Unix timestamps;
        issuer is the fixed string ``medwatch-api``.
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
    return jwt.encode(payload, _secret(), algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict | None:
    """Decode and validate a JWT.

    Returns the decoded payload on success, or ``None`` when the token
    is expired, malformed, signed with the wrong key, or carries the
    wrong issuer claim.
    """
    try:
        return jwt.decode(token, _secret(), algorithms=[JWT_ALGORITHM], issuer="medwatch-api")
    except jwt.PyJWTError:
        return None
