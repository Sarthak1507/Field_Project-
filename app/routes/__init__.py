"""Create and configure the Flask application."""
from pathlib import Path

from flask import Flask, jsonify, redirect, send_from_directory, url_for
from mysql.connector import Error as MySQLError, IntegrityError

from app.config import Config
from app.routes import register_blueprints


def create_app(test_config=None):
    root = Path(__file__).resolve().parent.parent
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["PROJECT_ROOT"] = root
    if test_config:
        app.config.update(test_config)

    register_blueprints(app)

    @app.errorhandler(ValueError)
    def invalid_input(error):
        return jsonify(error=str(error)), 400

    @app.errorhandler(IntegrityError)
    def constraint_conflict(error):
        if getattr(error, "errno", None) == 1062:
            message = "A record with one of these unique values already exists."
        elif getattr(error, "errno", None) in (1451, 1452):
            message = "This change conflicts with a related record. Review the linked records and try again."
        else:
            message = "The database rejected this change."
        return jsonify(error=message), 409

    @app.errorhandler(MySQLError)
    def database_unavailable(error):
        app.logger.error("MySQL operation failed: %s", error.__class__.__name__)
        return jsonify(error="The database is unavailable or could not complete the request."), 503

    # Keep the hand-built Phase 1 pages and assets intact while serving them
    # from the same origin as the JSON API.
    @app.get("/")
    def login_page():
        # Keep relative links in the existing HTML pages anchored under /frontend/.
        return redirect(url_for("frontend_page", page="index.html"))

    @app.get("/frontend/<path:page>")
    def frontend_page(page):
        allowed = {"index.html", "dashboard.html", "employees.html",
                   "employee-details.html", "employee-form.html",
                   "departments.html", "attendance.html", "leaves.html",
                   "salary.html", "users.html", "reports.html"}
        if page not in allowed:
            return jsonify(error="Page not found."), 404
        return send_from_directory(root / "frontend", page)

    @app.get("/assets/<path:filename>")
    def project_asset(filename):
        return send_from_directory(root / "assets", filename)

    return app