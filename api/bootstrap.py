"""Inject anggota1-5 folders into ``sys.path`` and lazy-load their modules.

The ``api/`` layer wraps but never modifies anggota1-5 source. When
a module fails to load (for example ``anggota3/BacaData.py`` has a
known SyntaxError that the team has agreed not to fix in their
file), :func:`get_module` returns ``None`` and the caller is
expected to fall back to an inline implementation.

The loader is memoised so repeated imports cost only a dict lookup,
and the per-call failure record is sticky for the lifetime of the
process to avoid retrying broken imports on every request.
"""
import sys
import importlib
import logging
from pathlib import Path
from typing import Any
from .config import ANGGOTA_DIRS

logger = logging.getLogger(__name__)

_loaded: dict[str, Any] = {}


def _inject_paths() -> None:
    """Prepend each existing ``anggota<n>`` directory to ``sys.path``.

    Works in both normal Python and PyInstaller frozen bundles. In a
    frozen app the anggota directories live under ``sys._MEIPASS``;
    the fallback path is used when the primary resolution fails.
    """
    for name, path in ANGGOTA_DIRS.items():
        p = str(path)
        if path.exists() and p not in sys.path:
            sys.path.insert(0, p)
            logger.info(f"injected {p}")
            continue
        # PyInstaller fallback: resolve under sys._MEIPASS.
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            meipass_path = str(Path(sys._MEIPASS) / name)
            if Path(meipass_path).exists() and meipass_path not in sys.path:
                sys.path.insert(0, meipass_path)
                logger.info(f"injected (MEIPASS) {meipass_path}")


def get_module(anggota: str, module_name: str) -> Any | None:
    """Resolve and cache an anggota submodule with graceful failure.

    Args:
        anggota: Owner namespace such as ``anggota2`` or ``anggota4``.
            Used only for the cache key and log line; the actual
            import is done by short name because the anggota folder
            has been added to ``sys.path``.
        module_name: Submodule short name (for example
            ``pasien_helper`` or ``safety_checker``).

    Returns:
        Imported module on success. ``None`` when the import raises;
        the failure is logged once and cached so subsequent calls
        do not re-attempt the broken import.
    """
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
