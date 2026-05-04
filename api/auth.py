"""Auth primitives: bcrypt password hashing, JWT issuance, JWT verification.

No Flask dependencies; unit-testable in isolation.
"""
import bcrypt
import jwt
from datetime import datetime, timezone, timedelta
from .config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRY_HOURS


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def issue_token(username: str, role: str, name: str) -> str:
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
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], issuer="medwatch-api")
    except jwt.PyJWTError:
        return None
