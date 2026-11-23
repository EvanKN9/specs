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

## Run tests

From the repository root, with the virtual environment active:

```powershell
python -m pytest backend\tests -q
```
