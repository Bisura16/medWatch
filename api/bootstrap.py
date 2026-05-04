"""Inject anggota1-5 folders into sys.path and lazy-load their modules with graceful fallback.

The api/ layer wraps but never modifies anggota1-5 source. If a module fails to load
(e.g. anggota3/BacaData.py has a known SyntaxError), get_module returns None and the
caller falls back to inline implementation.
"""
import sys
import importlib
import logging
from typing import Any
from .config import ANGGOTA_DIRS

logger = logging.getLogger(__name__)

_loaded: dict[str, Any] = {}


def _inject_paths() -> None:
    for name, path in ANGGOTA_DIRS.items():
        p = str(path)
        if path.exists() and p not in sys.path:
            sys.path.insert(0, p)
            logger.info(f"injected {p}")


def get_module(anggota: str, module_name: str) -> Any | None:
    """Returns the imported module or None if it failed to load."""
    _inject_paths()
    cache_key = f"{anggota}.{module_name}"
    if cache_key in _loaded:
        return _loaded[cache_key]
    try:
        mod = importlib.import_module(module_name)
        _loaded[cache_key] = mod
        return mod
    except Exception as e:
        logger.warning(f"failed to load {cache_key}: {e}")
        _loaded[cache_key] = None
        return None
