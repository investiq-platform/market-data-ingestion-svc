# market-data-ingestion-svc

FastAPI service for searching mutual-fund schemes, retrieving dated NAV history from
[MFAPI](https://www.mfapi.in/), and storing that data in PostgreSQL.

## Run the complete stack with Docker

Clone the entire repository (the Compose file builds both services), start Docker
Desktop, then run:

```bash
cd portfolio-mgmt-svc
docker compose up --build
```

This starts PostgreSQL on `5432`, this service on `8000`, and the Java GraphQL
service on `8080`. Stop the stack with `docker compose down`; this keeps the
database volume. Use `docker compose down -v` only to remove all local E2E data.

## Run locally

```bash
cp .env.example .env
python -m venv .venv
.venv/bin/pip install -e '.[dev]'
psql "$DATABASE_URL" -f db/schema.sql
.venv/bin/uvicorn app.main:app --reload
```

The service exposes:

- `GET /health`
- `GET /funds/search?q=axis` — searches live MFAPI scheme data
- `GET /funds/{scheme_code}/navs` — returns real, dated NAV records
- `POST /funds/{scheme_code}/ingest` — persists the latest full NAV history
- `GET /funds/{scheme_code}/stored-navs?limit=100` — reads persisted NAVs in
  descending date order; `limit` is between 1 and 500

`nav_history` has a composite primary key of `(scheme_code, nav_date)`. Ingestion
uses `INSERT ... ON CONFLICT`, so repeated synchronizations cannot create duplicate
NAV rows; unchanged records are left untouched.

Run the tests with `pytest`.
