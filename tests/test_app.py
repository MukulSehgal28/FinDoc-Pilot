# Run from the repository root with `python -m pytest` (plain `pytest` can fail to import `app`).
#
# Unit tests mock psycopg.connect, so they need no PostgreSQL and prove nothing about a real
# database. The last test is a real-database integration test and is opt-in.
import os
from unittest.mock import MagicMock, patch

import psycopg
import pytest
from dotenv import dotenv_values

from app import create_app


def make_client(database_url="postgresql://user:pw@host:5432/db"):
    return create_app({"TESTING": True, "DATABASE_URL": database_url}).test_client()


def test_health_works_without_database_url():
    response = make_client(database_url=None).get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_database_url_is_read_from_environment(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://from-env")
    assert create_app().config["DATABASE_URL"] == "postgresql://from-env"


def test_health_db_reports_missing_configuration():
    response = make_client(database_url=None).get("/health/db")
    assert response.status_code == 503
    assert "DATABASE_URL is not set" in response.get_json()["detail"]


def test_health_db_success():
    with patch("app.psycopg.connect") as connect:
        response = make_client("postgresql://u:p@h:1/d").get("/health/db")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}
    assert connect.call_args.args[0] == "postgresql://u:p@h:1/d"
    connect.return_value.__enter__.return_value.execute.assert_called_once_with("SELECT 1")


def test_health_db_failure_hides_internal_details():
    error = psycopg.OperationalError("password authentication failed for user secretuser at 10.0.0.5")
    with patch("app.psycopg.connect", side_effect=error):
        response = make_client().get("/health/db")
    assert response.status_code == 503
    assert response.get_json()["status"] == "error"
    assert "secretuser" not in response.get_data(as_text=True)
    assert "10.0.0.5" not in response.get_data(as_text=True)


def test_health_db_invalid_url_is_handled():
    # A malformed URL raises a psycopg error too; it must not become an HTTP 500.
    response = make_client("not-a-valid-url").get("/health/db")
    assert response.status_code == 503


# Opt-in: needs a running PostgreSQL and a valid DATABASE_URL in .env (or the environment).
# Run with:  $env:RUN_DB_INTEGRATION = "1"; python -m pytest -k real_database
@pytest.mark.skipif(os.environ.get("RUN_DB_INTEGRATION") != "1", reason="set RUN_DB_INTEGRATION=1 to run")
def test_health_db_against_real_database():
    url = os.environ.get("DATABASE_URL") or dotenv_values(".env").get("DATABASE_URL")
    assert url, "DATABASE_URL not found in the environment or .env"
    response = make_client(url).get("/health/db")
    assert response.status_code == 200
