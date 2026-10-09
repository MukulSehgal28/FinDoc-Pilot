# FinDoc-Pilot — Setup Guide (Milestone 1, Windows)

This is the single setup guide. Milestone 1 only provides a Flask app with two health endpoints and a
`DATABASE_URL`-driven PostgreSQL check. There is no schema, no models and no migrations yet.

Status values: **Completed automatically** · **Requires my action** · **Not applicable**.
Edit the status column yourself as you finish each step.

## 0. What was done for you and what was not

| Step | Status |
|---|---|
| Inspected the GitHub repo (only `.gitignore` and `README.md` existed) | Completed automatically |
| Drafted the Milestone 1 files (`requirements.txt`, `app/__init__.py`, `tests/test_app.py`, `.env.example`, `docs/DATABASE_DEBUG.md`, this file) | Completed automatically (delivered for review; **not** in your repo yet) |
| Smoke check of the routes against a stubbed database driver | Completed automatically (stub only; this is not the pytest suite and not a real database) |
| Add the files to your repository | Requires my action |
| Create the virtual environment and install dependencies | Requires my action |
| Create `.env` with my real connection details | Requires my action |
| Run `python -m pytest` and record the result | Requires my action |
| Verify real PostgreSQL connectivity | Requires my action |
| Commit and push | Requires my action (nothing was committed or pushed for you) |
| Schema, tables, migrations, Docker | Not applicable (none in Milestone 1) |

## 1. Prerequisites

| Prerequisite | How to verify | Status |
|---|---|---|
| Python 3.10 or newer (3.12 or 3.13 recommended) | `py -3 --version` | Requires my action |
| PostgreSQL installed and running | `Get-Service -Name "postgresql*"` should show `Running` | Requires my action |
| pgAdmin | Open it and connect to your server | Requires my action |
| Git and VS Code | `git --version`, `code --version` | Requires my action |

Both commands above only read state. Service names vary (for example `postgresql-x64-16`).

## 2. Environment setup (PowerShell, from the repository root)

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
code .env        # replace the placeholders; see section 3
```

If activation is blocked with "running scripts is disabled", either skip activation and prefix every command
with `.\.venv\Scripts\python.exe -m` (for example `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`),
or allow local scripts for your user once: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`.

Start the app:

```powershell
flask --app app run
```

Status: Requires my action. `.env` is already git-ignored, so it will not be committed.

## 3. PostgreSQL configuration (using pgAdmin)

Your connection string has this shape. Every value must come from your own machine:

```
DATABASE_URL=postgresql://DB_USER:DB_PASSWORD@DB_HOST:DB_PORT/DB_NAME
```

1. **Host, port, user:** in pgAdmin, right-click your server, choose *Properties*, then the *Connection* tab. Read
   *Host name/address*, *Port* and *Username*.
2. **Password:** the password for that user. pgAdmin may have saved it but does not display it. If it contains
   `@ : / # ? %`, URL-encode those characters (`@` becomes `%40`).
3. **Database name:** expand *Servers → your server → Databases* and pick the database you want the app to use.
4. **Only if no suitable database exists**, create one: right-click *Databases → Create → Database…*, enter a name,
   save. SQL equivalent, run in the Query Tool: `CREATE DATABASE <db_name>;`. This adds a new empty database and
   changes nothing existing.
5. **A dedicated user is optional.** You can use an existing user. If you prefer a least-privilege app user, run in
   the Query Tool (replace the placeholders, choose your own password):

   ```sql
   CREATE ROLE <db_user> LOGIN PASSWORD '<choose-a-password>';
   GRANT CONNECT ON DATABASE <db_name> TO <db_user>;
   ```

   `CONNECT` is all Milestone 1 needs, because the app only runs `SELECT 1`.
6. Put the values into `.env`, then test (inspection only; it changes nothing):

```powershell
python -c "import psycopg; from dotenv import dotenv_values; c = psycopg.connect(dotenv_values()['DATABASE_URL'], connect_timeout=3); print(c.execute('SELECT 1').fetchone()); c.close()"
```

Expected output: `(1,)`. On failure you get a full error here in your own terminal; see section 7 and
`docs/DATABASE_DEBUG.md`.

Status: Requires my action.

## 4. Schema and migrations

**No schema, tables, migrations or manual SQL are required in Milestone 1.** Do not run any schema SQL.
Flask-Migrate is intentionally not installed; add it when the first real models exist. Nothing in this guide
drops, resets or alters data. Status: Not applicable.

## 5. Verification

```powershell
python -m pytest
```

Use `python -m pytest`, not bare `pytest`, so the `app` package can be imported. This should run 6 tests that need no database and
skip 1 real-database test. Those 6 do not prove that PostgreSQL works.

Real-database integration test (opt-in, needs section 3 finished):

```powershell
$env:RUN_DB_INTEGRATION = "1"; python -m pytest -k real_database
Remove-Item Env:RUN_DB_INTEGRATION
```

With the app running (`flask --app app run`), in a second PowerShell window:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/health
Invoke-RestMethod http://127.0.0.1:5000/health/db
```

| Request | Expected | When |
|---|---|---|
| `/health` | `200` `{"status":"ok"}` | App is running (works with no database) |
| `/health/db` | `200` `{"status":"ok"}` | `SELECT 1` succeeded |
| `/health/db` | `503` with a `detail` saying `DATABASE_URL is not set` | `.env` missing or not filled in |
| `/health/db` | `503` with `Database connection failed` | Any connection problem. The real reason is printed in the Flask console, never sent to the client |

`Invoke-RestMethod` throws on a 503. The Flask console shows the real cause. Status: Requires my action.

## 6. Manual-action checklist (in order)

1. [ ] Create the files from this delivery in your repo at the paths shown. Apply the README link (below).
2. [ ] `py -3 -m venv .venv`, activate it, `pip install -r requirements.txt`.
3. [ ] Confirm the PostgreSQL service is `Running`.
4. [ ] In pgAdmin, collect host, port, user and database name (section 3). Create a database only if needed.
5. [ ] `Copy-Item .env.example .env` and fill in `DATABASE_URL`.
6. [ ] Run the connectivity one-liner from section 3; expect `(1,)`.
7. [ ] `python -m pytest`; save the exact output.
8. [ ] `flask --app app run`; check `/health` and `/health/db`.
9. [ ] Optionally run the opt-in integration test.
10. [ ] Review `git status` (confirm `.env` is not listed), then commit and push yourself.

## 7. Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| `py` or `python` not recognized | Python is not installed or not on PATH. Reinstall Python and tick "Add to PATH", or use `py -3`. |
| Activation: "running scripts is disabled" | See the note in section 2. |
| `ModuleNotFoundError: No module named 'app'` in pytest | Use `python -m pytest` from the repository root. |
| `ModuleNotFoundError: psycopg` or "no pq wrapper available" | Venv not active, or dependencies not installed: activate and run `pip install -r requirements.txt`. |
| pip finds no `psycopg-binary` wheel | Your Python is too new or old for a prebuilt wheel. Use Python 3.12 or 3.13. |
| `/health/db` says `DATABASE_URL is not set` | `.env` is missing, empty, or you launched Flask outside the repo root. |
| `Connection refused` | Service stopped or wrong port. Check `Get-Service -Name "postgresql*"` and the port in pgAdmin. |
| `password authentication failed` | Wrong user or password, or special characters not URL-encoded. |
| `database "..." does not exist` | Wrong name in the URL; create it (section 3, step 4) or fix the name. |
| `role "..." does not exist` | Wrong user in the URL. |
| `could not translate host name` | Typo in the host. |
| Timeout | Wrong host or blocked port. `Test-NetConnection <host> -Port <port>` inspects this. |
| `Address already in use` (Flask) | Another program uses port 5000. Run `flask --app app run --port 5001` and adjust the URLs above. |

More detail: `docs/DATABASE_DEBUG.md`.
