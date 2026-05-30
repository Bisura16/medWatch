"""Password policy and a bundled common-password blocklist.

Enforced server-side on registration and account creation. The
frontend strength meter is advisory only; this module is the
authority. The blocklist is a curated set of the most common leaked
passwords (offline-friendly, no network call to a breach API), plus
structural checks (length, repetition, username overlap).
"""
import re

MIN_LENGTH = 12

# Curated set of the most common leaked / trivially-guessable passwords.
# Stored lowercase; membership is checked case-insensitively. This is a
# pragmatic offline blocklist, not a full breach-corpus check.
_COMMON = frozenset(
    {
        "password", "passw0rd", "password1", "password12", "password123",
        "password1234", "passwordpassword", "qwertyuiop", "qwerty123",
        "1234567890", "123456789012", "12345678", "123456789", "1234567",
        "111111111111", "000000000000", "abcdefghijkl", "abc123456789",
        "iloveyou123", "letmein12345", "welcome12345", "admin1234567",
        "administrator", "qwertyuiop12", "asdfghjkl123", "zxcvbnm12345",
        "monkey123456", "dragon123456", "sunshine1234", "princess1234",
        "football1234", "baseball1234", "trustno1trust", "superman1234",
        "batman123456", "michael12345", "jordan123456", "harley123456",
        "loveme123456", "whatever1234", "freedom12345", "computer1234",
        "internet1234", "samsung12345", "starwars1234", "cheese123456",
        "indonesia123", "bismillah123", "rahasia12345", "kelompokb5lima",
        "medwatch1234", "medwatch12345", "polban123456", "qwerty1234567",
        "passw0rd1234", "p@ssw0rd1234", "iloveyouuuu1", "letmeinplease",
        "changeme1234", "default12345", "secret123456", "master123456",
        "sunshine0000", "00000000000a", "aaaaaaaaaaaa", "qwertyqwerty",
        "asdfasdfasdf", "1q2w3e4r5t6y", "zaq12wsx3edc", "1qaz2wsx3edc",
    }
)


def validate_password(password: str, username: str | None = None) -> tuple[bool, str]:
    """Validate a password against the policy.

    Args:
        password: Candidate plaintext password.
        username: Optional username to reject passwords that contain it.

    Returns:
        ``(True, "")`` when the password passes, otherwise
        ``(False, reason)`` with a human-readable Indonesian reason
        suitable for showing on the registration form.
    """
    if not password or not isinstance(password, str):
        return False, "Kata sandi wajib diisi."
    if len(password) < MIN_LENGTH:
        return False, f"Kata sandi minimal {MIN_LENGTH} karakter."
    if password.lower() in _COMMON:
        return False, "Kata sandi terlalu umum dan mudah ditebak. Pakai yang lain."
    if len(set(password)) < 4:
        return False, "Kata sandi terlalu monoton. Variasikan karakternya."
    if re.search(r"(.)\1{4,}", password):
        return False, "Hindari pengulangan karakter yang sama berturut-turut."
    if username and len(username) >= 3 and username.lower() in password.lower():
        return False, "Kata sandi tidak boleh mengandung nama pengguna."
    return True, ""


def password_strength(password: str) -> int:
    """Return a coarse 0-4 strength score mirroring the frontend meter.

    Used only as a convenience for callers; not part of policy
    enforcement. 0 = fails policy, 4 = strong.
    """
    ok, _ = validate_password(password)
    if not ok:
        return 0
    score = 1
    if len(password) >= 16:
        score += 1
    classes = sum(
        bool(re.search(p, password))
        for p in (r"[a-z]", r"[A-Z]", r"\d", r"[^A-Za-z0-9]")
    )
    if classes >= 3:
        score += 1
    if classes == 4 and len(password) >= 14:
        score += 1
    return min(score, 4)
