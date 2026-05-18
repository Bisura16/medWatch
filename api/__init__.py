"""Backend integration layer for MedWatch.

This package hosts the Flask API surface that wraps the read-only
teammate modules (``anggota1`` through ``anggota5``) and exposes them
to the Next.js frontend through HTTP endpoints. The package itself
is intentionally empty so submodules can be imported independently
without triggering heavy work at import time.
"""
