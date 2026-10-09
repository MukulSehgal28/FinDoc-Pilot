import os

import psycopg
from flask import Flask, jsonify


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)

    # DATABASE_URL is read but deliberately NOT required here, so the app (and /health)
    # starts even when the database is not configured. Only /health/db needs it.
    # `flask run` loads .env automatically (python-dotenv); tests pass test_config instead.
    app.config["DATABASE_URL"] = os.environ.get("DATABASE_URL")
    if test_config:
        app.config.update(test_config)

    @app.get("/health")
    def health():
        # Liveness only: proves Flask is running. Never touches the database.
        return jsonify(status="ok")

    @app.get("/health/db")
    def health_db():
        # Readiness: proves we can actually open a connection and run a query.
        url = app.config["DATABASE_URL"]
        if not url:
            return jsonify(
                status="error",
                detail="DATABASE_URL is not set. Copy .env.example to .env and fill it in "
                "(see SETUP_README.md).",
            ), 503

        try:
            # The `with` block commits and closes the connection. The short timeout stops
            # a wrong host or blocked port from hanging the request.
            with psycopg.connect(url, connect_timeout=3) as conn:
                conn.execute("SELECT 1")
        except psycopg.Error as exc:
            # The full error goes to the server console only (it helps debugging and libpq
            # messages do not contain the password). The client gets a generic message,
            # so hostnames, usernames and driver details are never exposed over HTTP.
            app.logger.error("Database check failed (%s): %s", type(exc).__name__, exc)
            return jsonify(
                status="error",
                detail="Database connection failed. See docs/DATABASE_DEBUG.md.",
            ), 503

        return jsonify(status="ok")

    return app
