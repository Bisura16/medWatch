"""Flask entry point. Registers blueprints, configures CORS, error handlers."""
import logging
import os
import sys
from pathlib import Path

# Allow `from api.config import ...` style imports both when running via gunicorn
# (cwd=/app/api) and when running locally via `flask --app app run`.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from api.config import CORS_ORIGINS, DEBUG, PORT, API_DIR
from api.routes import auth_routes, health
from api.routes import patient_routes, drug_routes, safety_routes
from api.routes import visualization_routes, pdf_routes, admin_routes


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__, static_folder=str(API_DIR / "static"), static_url_path="/static")

    CORS(app,
         origins=CORS_ORIGINS,
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    app.register_blueprint(health.bp)
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(patient_routes.bp)
    app.register_blueprint(drug_routes.bp)
    app.register_blueprint(safety_routes.bp)
    app.register_blueprint(visualization_routes.bp)
    app.register_blueprint(pdf_routes.bp)
    app.register_blueprint(admin_routes.bp)

    @app.route("/")
    def root():
        return send_from_directory(str(API_DIR / "static"), "index.html")

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        logger.exception("server error")
        return jsonify({"error": "internal server error"}), 500

    @app.after_request
    def strip_server_headers(response):
        response.headers.pop("Server", None)
        return response

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
