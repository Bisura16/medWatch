"""In-process rate limiting with lockout for auth endpoints.

Tracks failed attempts per key (username plus client IP) and locks the
key out for a cooldown once the threshold is crossed within the window.
Successful auth resets the counter.

This is in-memory and per-process, which is sufficient for the bundled
single-process desktop backend. On a multi-worker web deployment each
worker keeps its own counters (documented limitation); a shared store
would be required for strict cross-worker enforcement.
"""
import threading
import time
from collections import deque

# Defaults: 5 failures within 5 minutes triggers a 5 minute lockout.
_MAX_FAILURES = 5
_WINDOW_SECONDS = 300
_LOCKOUT_SECONDS = 300

_lock = threading.Lock()
_failures: dict[str, deque[float]] = {}
_locked_until: dict[str, float] = {}


def _now() -> float:
    return time.monotonic()


def check(key: str) -> tuple[bool, int]:
    """Return ``(locked, retry_after_seconds)`` for ``key``.

    Does not record an attempt; call :func:`record_failure` for that.
    """
    with _lock:
        until = _locked_until.get(key)
        if until is not None:
            remaining = until - _now()
            if remaining > 0:
                return True, int(remaining) + 1
            _locked_until.pop(key, None)
            _failures.pop(key, None)
        return False, 0


def record_failure(key: str) -> None:
    """Record one failed attempt and lock the key out past the threshold."""
    with _lock:
        now = _now()
        bucket = _failures.setdefault(key, deque())
        bucket.append(now)
        while bucket and now - bucket[0] > _WINDOW_SECONDS:
            bucket.popleft()
        if len(bucket) >= _MAX_FAILURES:
            _locked_until[key] = now + _LOCKOUT_SECONDS


def reset(key: str) -> None:
    """Clear all failure state for ``key`` after a successful auth."""
    with _lock:
        _failures.pop(key, None)
        _locked_until.pop(key, None)
