# Health Dashboard API

FastAPI microservice: package-by-feature at the top level, layered inside each
feature, Postgres-backed, Scalar API docs.

Single-tenant service that connects to a user's Garmin Connect account via the
[`garminconnect`](https://github.com/cyberjunky/python-garminconnect) package,
without ever persisting the account's username/password — only the resulting
session token is stored, and used to refresh daily stats afterwards.

---

## Quick start

```bash
git clone <this-repo> health-dashboard-api && cd health-dashboard-api/app

make install                       # creates ../.venv and installs [dev]
cp health_dashboard_service/.env.sample health_dashboard_service/.env
cp migrations/.env.sample migrations/.env
$EDITOR health_dashboard_service/.env      # point at your database

make migrate                       # apply migrations (requires goose)
make dev                           # http://127.0.0.1:8000/docs
```

`make help` lists every target.

### Manual setup

If you would rather not use `make`:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
cd app
pip install -e ".[dev]"
```

Note the `[dev]` extra — without it you get no pytest, ruff or mypy. Use
`.[test]` for a test-only install (this is what CI uses for the test job).

Never use `--break-system-packages`; it exists to bypass the guard that
protects your system Python, and it is never what you want here.

---

## Configuration

All settings come from the environment (see
`health_dashboard_service/.env.sample`), loaded and validated by
`pydantic-settings` in `health_dashboard_service/config.py`. Settings are
resolved lazily via `get_settings()`, so importing the package never requires
a populated environment — that keeps CI and unit tests simple.

| Variable | Default | Notes |
| --- | --- | --- |
| `PG_HOST` / `PG_USER` / `PG_PASSWORD` / `PG_DATABASE` | — | Required |
| `PG_PORT` | `5432` | |
| `ENVIRONMENT` | `development` | `development` \| `staging` \| `production` |
| `LOG_LEVEL` | `INFO` | |
| `CORS_ALLOW_ORIGINS` | `[]` | JSON array. Empty disables the middleware |
| `DB_POOL_SIZE` / `DB_MAX_OVERFLOW` | `5` / `10` | |
| `DB_POOL_RECYCLE` | `1800` | Seconds before a pooled connection is recycled |

Real `.env` files are gitignored; only `.env.sample` is committed.

---

## Running

```bash
make dev        # reload enabled
make run        # production-style
make docker-build && docker run -p 8000:8000 --env-file health_dashboard_service/.env health-dashboard-api:local
```

| Endpoint | Purpose |
| --- | --- |
| `/docs` | Scalar API reference |
| `/openapi.json` | OpenAPI schema |
| `/health` | Liveness — touches no dependencies |
| `/health/ready` | Readiness — checks Postgres, 503 when unreachable |
| `POST /garmin/authenticate` | Exchange Garmin credentials for a stored session token |
| `POST /garmin/refresh` | Pull and upsert one day's summary stats using the stored session |

The app verifies database connectivity during startup, so bad credentials fail
the deploy rather than the first user request.

`routes/garmin.py`'s two handlers are synchronous (`def`, not `async def`) —
`garminconnect` is a synchronous SDK, so these two endpoints don't propagate
client-disconnect cancellation the way the rest of the API does; this is an
accepted, scoped limitation (see `.standards/endpoint-standards.md`).

---

## Testing

```bash
make test           # pytest -v
make test-cov       # with coverage
make check          # lint + typecheck + test, same as CI
```

Discovery conventions (configured in `pyproject.toml`):

| Kind | File | Class |
| --- | --- | --- |
| Unit | `*_tests.py` | `*Tests` |
| Service | `*_feature.py` | `*Feature` |

```bash
pytest tests/unit               # a folder
pytest -x                       # stop at first failure
pytest --collect-only           # show what would run
```

Unit tests cover validations, mappings and helpers. Service tests drive the
`/garmin/*` endpoints against a real Postgres via TestContainers, mocking only
the `garminconnect`-facing boundary (`infrastructure/garmin/garmin_client_factory.py`)
— `garminconnect` itself is trusted and never mocked.

Object generation uses polyfactory behind `GarminAutoFixture.generate(Type,
**overrides)` — pin the fields a test cares about, leave the rest anonymous.

---

## Migrations

[goose](https://github.com/pressly/goose) SQL migrations in `app/migrations/`.

```bash
cd app/migrations
goose create add_widget_table sql   # new migration
goose up
goose down
```

Every migration needs a working `-- +goose Down`; CI applies `up`, `down-to 0`,
then `up` again to prove rollbacks are real.

---

## Layout

```
app/
  health_dashboard_service/
    config.py                  Settings (pydantic-settings)
    main.py                    create_app(): middleware, handlers, routers
    contracts/                 Wire models. ApiModel gives camelCase aliases
    routes/                    HTTP layer, auto-discovered
    features/<feature>/
      domain/                  Business logic; owns the unit of work
      persistence/             SQL reader/writer + row entities
      <feature>_mapper.py      contract <-> domain <-> persistence
    infrastructure/
      http/                    Exception handlers
      postgres/                Engine and unit of work
      garmin/                  Synchronous wrapper around `garminconnect`
    openapi/                   Shared tags, response declarations, schema
  migrations/                  goose SQL
  tests/
```

### Adding a feature

1. `health_dashboard_service/features/<feature>/` with `domain/` and `persistence/`.
2. A mapper — persistence entities and wire contracts must not meet directly.
3. `health_dashboard_service/routes/<feature>.py` exposing `router`. Auto-discovery
   picks it up; no registration needed.
4. Contracts extend `ApiModel` so serialisation stays camelCase.
5. Tests: `*_tests.py` for units, `*_feature.py` for routes.

### Conventions worth keeping

- **The domain owns the unit of work.** Every domain function opens one with
  `async with create_persistence_controller() as pc:` and the block disposes it.
  Routes stay free of persistence concerns.
- **Commit explicitly, release automatically.** `save_changes()` commits and
  does not close; leaving the `async with` rolls back if nothing committed and
  always returns the connection to the pool.
- **Every paged query needs a total `ORDER BY`.** Postgres gives no stability
  guarantee for `LIMIT/OFFSET` without one.
- **Bound every page size.** `MAX_PAGE_SIZE` is enforced in the contract.
- **Parameterise all SQL.** No f-strings around user input, ever.

---

## Dependencies

`pyproject.toml` holds bounded ranges; `requirements.lock` and
`requirements-dev.lock` hold exact pins and are what Docker and CI install.

```bash
make lock     # regenerate after changing pyproject dependencies
```

Resolution runs inside `python:3.14-slim` — the same base image the Dockerfile
uses — so the lock matches what production actually gets.

---

## CI

`.github/workflows/ci.yml` runs on every push and PR:

- **quality** — ruff lint, ruff format check, mypy
- **test** — pytest on 3.14 with coverage
- **migrations** — goose up / down-to 0 / up against real Postgres
- **docker** — builds the image and smoke-tests `/health` and `/health/ready`

Install the local hooks with `pre-commit install`.
