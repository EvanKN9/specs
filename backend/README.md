# SPECS backend

This is the first backend milestone: a minimal FastAPI application with a versioned health endpoint and local Vite CORS support. Persistence, catalog, compatibility, optimization, and LLM features are intentionally not included yet.

## Windows PowerShell setup

From the repository root:

```powershell
py -3 -m venv backend\.venv
& .\backend\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements-dev.txt
```

If PowerShell blocks activation for the current user, run this once in PowerShell and then activate again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Copy the safe example configuration if you want a local `.env` reference:

```powershell
Copy-Item backend\.env.example backend\.env
```

The application currently reads configuration from environment variables. The example values are also the built-in defaults, so no `.env` loader or credentials are required for this milestone.

## Run the backend

From the repository root, with the virtual environment active:

```powershell
python -m uvicorn app.main:app --app-dir backend --reload
```

The API is available at `http://127.0.0.1:8000`, and the health endpoint is `http://127.0.0.1:8000/api/v1/health`.

## Database migrations

Set `DATABASE_URL` in `backend\.env` or the current PowerShell session. Use the local `specs_dev` database only. The committed example uses a placeholder password and must not be used as a real credential.

Verify the configured database name without printing the full URL:

```powershell
python -c "from backend.app.config import Settings; from sqlalchemy.engine import make_url; print(make_url(Settings.from_environment().database_url).database)"
```

The command must print:

```text
specs_dev
```

After that verification, apply the initial non-destructive migration:

```powershell
alembic -c backend\alembic.ini upgrade head
```

Check the migration version:

```powershell
alembic -c backend\alembic.ini current
```

The initial migration creates only the `components` table and Alembic’s version table. It does not reset or modify the `blog` database.

## Run tests

From the repository root, with the virtual environment active:

```powershell
python -m pytest backend\tests -q
```

The database tests use an isolated in-memory SQLite database; they do not require or modify PostgreSQL.
