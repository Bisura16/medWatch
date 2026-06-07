"""Desktop entry point for the MedWatch Flask backend.

Activates only when ``MEDWATCH_DESKTOP=1`` is set. Binds to
``127.0.0.1`` on an OS-assigned ephemeral port and writes the
line ``MEDWATCH_BACKEND_PORT=<n>`` to stdout so that the Electron
main process can parse it and target subsequent HTTP requests.

The web and cloud entry paths (gunicorn worker, ``flask run``,
``python -m api.app``) are unaffected because this module is only
referenced by the PyInstaller spec and is never imported by
``api/app.py``.
"""
import logging
import os
import sys
from wsgiref.simple_server import WSGIServer, make_server


def _resolve_db_path() -> str:
    """Return the validated SQLite path passed by Electron via MEDWATCH_DB_PATH.

    Fails loudly (RuntimeError, which exits the backend non-zero so the
    Electron shell shows an error dialog) when the path is missing, the
    file is absent or unreadable, or it has no ``drugs`` table. A missing
    or empty catalog is never allowed to start up and silently serve
    nothing.

    Raises:
        RuntimeError: When the env var is missing, the file is absent or
            unreadable, or the database has no ``drugs`` table.
    """
    db = os.environ.get("MEDWATCH_DB_PATH")
    if not db:
        raise RuntimeError(
            "MEDWATCH_DB_PATH is required when running in desktop mode."
        )
    if not os.path.isfile(db):
        raise RuntimeError(
            f"Database obat tidak ditemukan di {db}. Ulangi instalasi aplikasi."
        )
    import sqlite3
    try:
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=5)
        try:
            n = con.execute(
                "SELECT COUNT(*) FROM sqlite_master "
                "WHERE type='table' AND name='drugs'"
            ).fetchone()[0]
        finally:
            con.close()
    except sqlite3.Error as e:
        raise RuntimeError(f"Database obat di {db} tidak terbaca: {e}")
    if not n:
        raise RuntimeError(
            f"Database obat di {db} tidak punya tabel drugs. "
            "Ulangi instalasi aplikasi."
        )
    return db


def _print_port(port: int) -> None:
    """Emit the port handshake line and flush stdout immediately."""
    sys.stdout.write(f"MEDWATCH_BACKEND_PORT={port}\n")
    sys.stdout.flush()


def main() -> int:
    """Run the bundled Flask backend in desktop mode.

    Returns:
        Exit code. ``0`` on clean shutdown via SIGINT, ``2`` when the
        guard env var is not set (caller invoked this entry point
        outside the desktop pipeline).
    """
    if os.environ.get("MEDWATCH_DESKTOP") != "1":
        sys.stderr.write(
            "desktop_entry.py is for MEDWATCH_DESKTOP=1 only.\n"
        )
        return 2

    db_path = _resolve_db_path()
    os.environ["MEDWATCH_DB_PATH_RESOLVED"] = db_path

    # Import after env validation so any import-time failure surfaces
    # only when the env contract has been honored. Lazy import also
    # speeds up the failure path above.
    from api.app import create_app

    app = create_app()

    server: WSGIServer = make_server("127.0.0.1", 0, app)
    port = server.server_address[1]

    _print_port(port)

    logging.getLogger(__name__).info(
        "MedWatch backend ready on 127.0.0.1:%d (desktop mode)", port
    )

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
