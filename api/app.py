"""Flask entry point for the MedWatch backend.

Builds the Flask application, registers every route blueprint,
applies the CORS allowlist, wires global error handlers, and
strips the ``Server`` response header to reduce fingerprinting.

The module exposes both a ``create_app`` factory (used by tests
and by Cloud Run gunicorn workers) and a module-level ``app``
instance that legacy entry points still import directly.
"""
import logging
import os
import sys
from pathlib import Path

# Allow `from api.config import ...` style imports both when running via gunicorn
# (cwd=/app/api) and when running locally via `flask --app app run`.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from api.config import CORS_ORIGINS, DEBUG, PORT, API_DIR, RENDERER_DIR
from api.routes import auth_routes, health
from api.routes import patient_routes, drug_routes, safety_routes
from api.routes import visualization_routes, pdf_routes, admin_routes
from api.storage import ensure_seeded


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _register_renderer(app: Flask) -> None:
    """Serve the bundled Next.js static export as a loopback SPA (desktop).

    Resolves trailingSlash routes (``/login/`` -> ``login/index.html``),
    serves ``/_next`` assets and root files, and falls back to the root
    ``index.html`` for unknown non-API paths so the client router can
    take over. ``/api/*`` paths are never intercepted; an unknown one
    yields the JSON 404 from the error handler.
    """
    renderer = RENDERER_DIR

    def _send(rel: str):
        return send_from_directory(str(renderer), rel)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_renderer(path: str):
        if path.startswith("api/") or path == "api":
            return jsonify({"error": "not found"}), 404
        candidate = renderer / path
        if path and candidate.is_file():
            return _send(path)
        index_in_dir = renderer / path / "index.html"
        if index_in_dir.is_file():
            return _send(f"{path}/index.html" if path else "index.html")
        html_file = renderer / f"{path}.html"
        if path and html_file.is_file():
            return _send(f"{path}.html")
        # SPA fallback: boot the app shell so the client router can route.
        if (renderer / "index.html").is_file():
            return _send("index.html")
        return jsonify({"error": "not found"}), 404


def create_app() -> Flask:
    """Build and return a fully wired Flask application.

    Registers the eight route blueprints, attaches CORS with the
    configured allowlist, defines the static index route, and
    installs 404 / 500 JSON error handlers plus an ``after_request``
    hook that removes the ``Server`` header.

    Returns:
        Configured ``flask.Flask`` instance ready to serve requests.
    """
    app = Flask(__name__, static_folder=str(API_DIR / "static"), static_url_path="/static")

    # Only trust X-Forwarded-For when explicitly running behind a known proxy
    # (Cloud Run sets MEDWATCH_TRUST_PROXY=1). On desktop/local there is no
    # trusted proxy, so honoring a client-supplied XFF would let an attacker
    # rotate it to evade the per-ip login rate limit; keep the real peer there.
    if os.environ.get("MEDWATCH_TRUST_PROXY", "").lower() in ("1", "true", "yes"):
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)

    CORS(app,
         origins=CORS_ORIGINS,
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         expose_headers=["X-Total-Count"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    app.register_blueprint(health.bp)
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(patient_routes.bp)
    app.register_blueprint(drug_routes.bp)
    app.register_blueprint(safety_routes.bp)
    app.register_blueprint(visualization_routes.bp)
    app.register_blueprint(pdf_routes.bp)
    app.register_blueprint(admin_routes.bp)

    # Seed the writable data dir from the bundled seed on first desktop launch
    # (no-op in web/dev where DATA_DIR == SEED_DIR).
    ensure_seeded()

    if RENDERER_DIR is not None:
        _register_renderer(app)
    else:
        @app.route("/")
        def root():
            """Serve the bundled API landing page (web/cloud mode)."""
            return send_from_directory(str(API_DIR / "static"), "index.html")

    @app.errorhandler(404)
    def not_found(e):
        """Return a JSON-shaped 404 instead of the default HTML body."""
        return jsonify({"error": "not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        """Log the traceback and return a JSON 500 without exposing internals."""
        logger.exception("server error")
        return jsonify({"error": "internal server error"}), 500

    @app.after_request
    def strip_server_headers(response):
        """Drop the ``Server`` header on every response to reduce fingerprinting."""
        response.headers.pop("Server", None)
        return response

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
