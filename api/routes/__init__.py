"""Flask blueprint route handlers for the MedWatch API.

Each module in this package registers one ``flask.Blueprint`` that
groups a related set of HTTP endpoints (health, auth, patients,
drugs, safety, visualizations, PDF generation, admin). The
blueprints are wired into the Flask app in ``api.app.create_app``.
"""
