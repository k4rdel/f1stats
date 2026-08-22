*Read this in other languages: [English](README.en.md), [Polski](README.md).*

---

# F1 Stats

> An asynchronous API for exploring Formula 1 driver statistics, comparing results, and browsing season calendars.

[![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-ready-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/license-private-lightgrey)](#)

F1 Stats combines data from the [Jolpica F1 API](https://api.jolpi.ca/ergast/f1/) with a local database. When the application receives a request for a driver or season, it checks the cache first and fetches missing data from the external API only when needed.

## What does it do?

- fetches and caches driver statistics,
- displays the race calendar for a selected season,
- compares two drivers in a single response,
- calculates win percentage, pole positions, podiums, hat-tricks, and average starting and finishing positions,
- limits request volume with `slowapi`,
- runs asynchronously with FastAPI, SQLAlchemy, and `httpx`.

## Quick start with Docker

### 1. Prepare the configuration

```bash
cp .env.example .env
```

Set the PostgreSQL credentials and the database URL in `.env`:

```dotenv
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_database
DATABASE_URL=postgresql+psycopg://your_user:your_password@db:5432/your_database
```

### 2. Start the API and database

```bash
docker compose up --build
```

The application will be available at `http://localhost:80`.

On the first run, migrations and the optional backfill can be executed with:

```bash
docker compose exec app ./scripts/migrate.sh
```

> `scripts/migrate.sh` runs `alembic upgrade head` followed by `scripts/backfill.py`. The backfill may send requests to the Jolpica F1 API.

## Local development

Python 3.14 and a running PostgreSQL instance are required.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

When running outside Docker, point the database URL to `localhost`:

```dotenv
DATABASE_URL=postgresql+psycopg://chagneit:chagneit@localhost:5432/chagneit
```

Run the migrations and start the development server:

```bash
alembic upgrade head
fastapi dev app/main.py
```

The API will be available at `http://127.0.0.1:80`.

## Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | Basic health check |
| `GET` | `/drivers` | List of drivers currently stored in the cache |
| `GET` | `/drivers/{driver_id}` | Driver statistics; missing data is fetched from Jolpica |
| `GET` | `/races/{season}` | Races for a season; missing seasons are cached |
| `GET` | `/compare/{driver1}/{driver2}` | Comparison of two drivers |

### Example requests

```bash
curl http://localhost:80/drivers/leclerc
curl http://localhost:80/races/2024
curl http://localhost:80/compare/leclerc/max_verstappen
```

Example response for `/drivers/leclerc`:

```json
{
  "driverId": "leclerc",
  "name": "Charles",
  "lastName": "Leclerc",
  "driverNumber": "16",
  "nationality": "Monegasque",
  "winningPercentage": 12.5,
  "hatTricks": 0,
  "poles": 26,
  "podiums": 48,
  "avgStartPosition": 6.2,
  "avgEndPosition": 6.8
}
```

## API documentation

Once the application is running, FastAPI provides interactive documentation:

- Swagger UI: [`/docs`](http://localhost:80/docs)
- ReDoc: [`/redoc`](http://localhost:80/redoc)

## Rate limits

Endpoints are protected by `slowapi` and use the following limits:

- `15/minute`: `/`, `/drivers`, `/races/{season}`,
- `10/minute`: `/drivers/{driver_id}`, `/compare/{driver1}/{driver2}`.

When the limit is exceeded, the API returns `429 Too Many Requests`.

## Tests

Tests use an isolated SQLite database:

```bash
pytest
```

## Project structure

```text
.
├── app/                 # FastAPI application package
│   ├── main.py          # Endpoints and caching logic
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic response models
│   ├── database.py       # Database engine and sessions
│   └── utils.py          # F1 statistics calculations
├── scripts/             # Operational scripts
│   ├── backfill.py       # Data backfill script
│   └── migrate.sh        # Migrations + backfill
├── tests/               # Application tests
│   └── test_main.py      # Endpoint tests
├── alembic/              # Migration history
├── docker-compose.yml    # PostgreSQL + API
└── requirements.txt      # Python dependencies
```

## Stack

- **FastAPI** + **Uvicorn** - HTTP layer and OpenAPI documentation,
- **SQLAlchemy async** - database access,
- **PostgreSQL** - database started by Docker Compose,
- **Alembic** - schema versioning,
- **Pydantic** - response validation,
- **httpx** - asynchronous communication with Jolpica,
- **slowapi** - rate limiting.

## Roadmap

- frontend for visualizing statistics and comparisons,
- more filters for seasons and drivers,
- integration tests with a mocked Jolpica API,
- API monitoring and metrics.

## Data source

Historical data is fetched from the [Jolpica F1 API](https://api.jolpi.ca/ergast/f1/), the successor to the Ergast Developer API. F1 Stats is not an official Formula 1 product.
