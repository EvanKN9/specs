# SPECS backend

This backend provides the SPECS foundation and Milestone 1D catalog: a versioned FastAPI API, PostgreSQL persistence, an idempotent TechFuelHQ import, six supplemental CPU coolers, and read-only component endpoints. Compatibility, optimization, authentication, and LLM features are intentionally not included yet.

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

## Import the component dataset

The importer downloads `https://techfuelhq.com/data/pc-builder-parts.json`, validates the configured database name is `specs_dev`, and upserts by the source dataset name plus original component ID:

```powershell
python -m backend.scripts.import_components
```

To repeat an import from an already downloaded JSON file:

```powershell
python -m backend.scripts.import_components --input path\to\pc-builder-parts.json
```

The source is CC BY 4.0 and requires TechFuelHQ attribution. The importer preserves source IDs, source URLs, verification dates, attribution, and license metadata. The source dataset contains seven categories (CPU, GPU, motherboard, RAM, storage, PSU, and case); RAM is normalized to `memory`. Six CPU-cooler records are maintained separately in `backend\data\cpu_coolers.json` from manufacturer documentation and are labeled as supplemental. No cooler specifications are generated from estimates.

The same command applies `backend\data\demo_pricing.json`, a separate, non-live fixture. It assigns illustrative USD values to the catalog and sets `price_is_illustrative=true` plus the fixture name in `price_source`. These are not live prices and are not verified retailer prices. Hardware specifications remain in the `specifications` JSON field and are not derived from the pricing fixture.

The imported data is sufficient for future deterministic checks involving many CPU/socket, motherboard/socket and RAM-type combinations, PSU wattage, case form factor, selected GPU lengths, storage interfaces, and cooler socket/height data. Important gaps remain: some GPU board lengths and PSU minimums are absent, many storage endurance values are absent, most case GPU-clearance values are absent, RAM rank is absent, and BIOS support, QVL, lane sharing, connector requirements, exact slot availability, and full cooler/RAM clearance are not complete. These gaps must remain explicit until sourced.

## Catalog API

```text
GET /api/v1/components?category=cpu&offset=0&limit=20
GET /api/v1/components/{id}
```

Category is optional. `limit` is bounded from 1 through 100, and missing component IDs return 404.

## Run tests

From the repository root, with the virtual environment active:

```powershell
python -m pytest backend\tests -q
```

The database tests use an isolated in-memory SQLite database; they do not require or modify PostgreSQL.
