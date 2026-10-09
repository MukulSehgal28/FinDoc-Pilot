# Database Debugging Reference

Practical guide for troubleshooting the PostgreSQL connection. It is not a database dump. Never paste
passwords, full connection strings or real data into this file, an issue or an LLM chat.

## Known facts (from the code in this repo)

- Environment variable: `DATABASE_URL` only. Placeholder form: `postgresql://DB_USER:DB_PASSWORD@DB_HOST:DB_PORT/DB_NAME`.
  Real values live only in your local, git-ignored `.env`.
- Driver: `psycopg` 3 (`psycopg[binary]`) used directly. No ORM, no SQLAlchemy, no Flask-Migrate yet.
- Connection flow: `create_app()` in `app/__init__.py` reads `DATABASE_URL` (missing is allowed) →
  `GET /health/db` opens a connection with a 3-second timeout, runs `SELECT 1`, closes it.
  The connection is opened per request; nothing runs at startup.
- Responses: success `200 {"status":"ok"}`. Missing config `503` with `DATABASE_URL is not set`. Any psycopg error
  `503` with a generic message. The real error is logged to the Flask console only.
- Schema and migrations: **none.** No tables, no models, no migration folder. Migrations are revisited when the
  first real models exist.

## Unverified (update when confirmed)

- Live connectivity to your PostgreSQL instance has not been tested by anyone yet.
- The pytest results have not been recorded yet. The unit tests mock the driver.

## Commands

Inspect only (change nothing):

| Purpose | Command |
|---|---|
| Is the service running? | `Get-Service -Name "postgresql*"` |
| Is the port reachable? | `Test-NetConnection localhost -Port <port>` (use your host and port) |
| Does the URL work? | the Python one-liner in `SETUP_README.md` section 3 |
| Unit tests (mocked) | `python -m pytest` |
| Real-database test (opt-in) | `$env:RUN_DB_INTEGRATION = "1"; python -m pytest -k real_database` |
| Connection settings | pgAdmin: server → *Properties → Connection* |

Changes state (use deliberately):

| Command | Effect |
|---|---|
| `CREATE DATABASE <db_name>;` | Adds a new empty database |
| `CREATE ROLE <db_user> LOGIN PASSWORD '...'` | Adds a login role |
| `GRANT CONNECT ON DATABASE <db_name> TO <db_user>;` | Changes permissions |
| Starting or stopping the PostgreSQL service | Interrupts every client |

## Safe diagnostic SQL (read-only; run in the pgAdmin Query Tool)

```sql
SELECT 1;
SELECT version();
SELECT current_database(), current_user;
SHOW port;
SELECT datname FROM pg_database WHERE NOT datistemplate;   -- does my database exist?
SELECT rolname FROM pg_roles WHERE rolcanlogin;            -- does my user exist? (no password data)
```

No application tables exist yet, so there is nothing else to query.

## Common failures

| Message (shown in the Flask console or your terminal) | Layer | Fix |
|---|---|---|
| `DATABASE_URL is not set` | Config | Create `.env` from `.env.example`; run Flask from the repo root. |
| `connection refused` | Server/port | Start the service; confirm the port in pgAdmin. |
| `password authentication failed` | Auth | Check user and password; URL-encode special characters. |
| `database "x" does not exist` | Database | Fix the name or create the database (changes state). |
| `role "x" does not exist` | Auth | Fix the user. |
| `could not translate host name` | Network | Fix the host spelling. |
| timeout / `connection timeout expired` | Network | Wrong host or blocked port. |
| `no pg_hba.conf entry` | Server config | Server-side access rule. Edit it only if you understand it, and do so with care. |
| `ModuleNotFoundError: psycopg` / `no pq wrapper` | Python env | Activate the venv; `pip install -r requirements.txt`. |
| invalid URL / missing `=` | Config | Check the URL format and that special characters are encoded. |

## Debugging workflow

1. Reproduce: call `/health/db`, or run the Python one-liner.
2. Collect the real error from the Flask console or one-liner. Remove passwords, hostnames and usernames before
   sharing it anywhere.
3. Identify the layer: config → Python environment → network/port → authentication → database.
4. Isolate: test the same URL in pgAdmin or the one-liner outside Flask.
5. Make the smallest fix (one change at a time).
6. Run `python -m pytest`, then re-check `/health/db`.

## Data safety

Never drop, reset, truncate or recreate a database as a troubleshooting shortcut, and never edit PostgreSQL's
server configuration without a backup and a clear reason. Connection problems are almost always configuration.
