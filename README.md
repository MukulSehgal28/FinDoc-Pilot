# FinDoc-Pilot

A tool for discovering and collecting publicly available financial documents
(annual reports, filings) for companies, so they can be analysed later.

## Current scope — Milestone 1 (foundation)

This branch, `milestone/01-foundation`, contains **only the application
foundation and health-check endpoints**. It is intentionally minimal.

**Milestone 1 does NOT include:** database schemas, migrations, ORM models,
web crawling, document downloading, or any financial-document processing.
Those arrive in later milestones.

## Health endpoints

The app exposes two endpoints:

| Endpoint | Type | Behaviour |
|---|---|---|
| `GET /health` | Liveness | `200 {"status":"ok"}` — proves Flask is running. **Never touches the database.** |
| `GET /health/db` | Readiness | `200 {"status":"ok"}` when `DATABASE_URL` points to a reachable PostgreSQL database (runs `SELECT 1`). Returns `503` with a safe message if the URL is missing or the connection fails — credentials and internal details are never sent to the client. |

## Setup (Windows)

Requires Python 3.10+ (3.12/3.13 recommended) and a running PostgreSQL server.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

Copy-Item .env.example .env
code .env          # replace the placeholders with your real PostgreSQL values

flask --app app run
```

Then check the endpoints in a second PowerShell window:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/health
Invoke-RestMethod http://127.0.0.1:5000/health/db
```

## Run the tests

```powershell
python -m pytest
```

Use `python -m pytest` (not bare `pytest`) so the `app` package imports correctly.
The default suite is hermetic: it mocks the database driver and needs no
PostgreSQL. One real-database integration test is opt-in:

```powershell
$env:RUN_DB_INTEGRATION = "1"; python -m pytest -k real_database
```

## Further documentation

- **[SETUP_README.md](SETUP_README.md)** — full step-by-step setup, PostgreSQL
  configuration via pgAdmin, verification, and troubleshooting.
- **[docs/DATABASE_DEBUG.md](docs/DATABASE_DEBUG.md)** — PostgreSQL connection
  debugging reference (read-only commands, common failures, data-safety rules).

## Stack

Python · Flask 3 · `psycopg` 3 (direct SQL; no ORM yet) · `python-dotenv` · pytest
