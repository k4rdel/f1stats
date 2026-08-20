# F1 Stats

> Asynchroniczne API do odkrywania statystyk kierowców Formuły 1, porównywania ich wyników i przeglądania kalendarza sezonów.

[![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-ready-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/license-private-lightgrey)](#)

F1 Stats łączy dane z [Jolpica F1 API](https://api.jolpi.ca/ergast/f1/) z lokalną bazą danych. Gdy aplikacja otrzyma zapytanie o kierowcę albo sezon, najpierw sprawdza cache, a dopiero potem pobiera brakujące dane z zewnętrznego API.

## Co potrafi?

- pobierać i cache'ować statystyki kierowców,
- pokazywać kalendarz wybranego sezonu,
- porównywać dwóch kierowców w jednym response,
- wyliczać procent zwycięstw, pole position, podia, hat-tricki oraz średnie pozycje startu i mety,
- ograniczać liczbę zapytań dzięki `slowapi`,
- działać asynchronicznie dzięki FastAPI, SQLAlchemy i `httpx`.

## Szybki start z Dockerem

### 1. Przygotuj konfigurację

```bash
cp .env.example .env
```

W `.env` ustaw dane PostgreSQL oraz URL używany przez aplikację:

```dotenv
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_database
DATABASE_URL=postgresql+psycopg://your_user:your_password@db:5432/your_database
```

### 2. Uruchom API i bazę

```bash
docker compose up --build
```

Aplikacja będzie dostępna pod adresem `http://localhost:80`.

Przy pierwszym uruchomieniu migracje i opcjonalny backfill można wykonać skryptem:

```bash
docker compose exec app ./migrate.sh
```

> `migrate.sh` uruchamia `alembic upgrade head`, a następnie `backfill.py`. Backfill może wykonywać zapytania do Jolpica F1 API.

## Uruchomienie lokalne

Wymagany jest Python 3.14 oraz działający PostgreSQL.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Dla uruchomienia poza Dockerem ustaw host bazy na `localhost`:

```dotenv
DATABASE_URL=postgresql+psycopg://chagneit:chagneit@localhost:5432/chagneit
```

Następnie wykonaj migracje i uruchom serwer deweloperski:

```bash
alembic upgrade head
fastapi dev main.py
```

API będzie działać pod `http://127.0.0.1:80`.

## Endpointy

| Metoda | Endpoint | Opis |
| --- | --- | --- |
| `GET` | `/` | Prosty health check |
| `GET` | `/drivers` | Lista kierowców zapisanych w cache |
| `GET` | `/drivers/{driver_id}` | Statystyki kierowcy; brakujące dane są pobierane z Jolpica |
| `GET` | `/races/{season}` | Wyścigi wskazanego sezonu; brakujący sezon jest cache'owany |
| `GET` | `/compare/{driver1}/{driver2}` | Porównanie dwóch kierowców |

### Przykładowe zapytania

```bash
curl http://localhost:80/drivers/leclerc
curl http://localhost:80/races/2024
curl http://localhost:80/compare/leclerc/max_verstappen
```

Przykładowy response dla `/drivers/leclerc`:

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

## Dokumentacja API

Po uruchomieniu aplikacji FastAPI udostępnia interaktywną dokumentację:

- Swagger UI: [`/docs`](http://localhost:80/docs)
- ReDoc: [`/redoc`](http://localhost:80/redoc)

## Limity zapytań

Endpointy są chronione przez `slowapi` i mają następujące limity:

- `15/minute`: `/`, `/drivers`, `/races/{season}`,
- `10/minute`: `/drivers/{driver_id}`, `/compare/{driver1}/{driver2}`.

Po przekroczeniu limitu API zwraca błąd `429 Too Many Requests`.

## Testy

Testy korzystają z izolowanej bazy SQLite:

```bash
pytest
```

## Struktura projektu

```text
.
├── main.py              # endpointy FastAPI i logika cache'owania
├── models.py            # modele SQLAlchemy
├── schemas.py           # modele response Pydantic
├── database.py          # silnik i sesje bazy danych
├── utils.py             # obliczenia statystyk F1
├── backfill.py          # uzupełnianie danych
├── migrate.sh           # migracje + backfill
├── alembic/              # historia migracji
├── docker-compose.yml    # PostgreSQL + API
└── test_main.py          # testy endpointów
```

## Stack

- **FastAPI** + **Uvicorn** - warstwa HTTP i dokumentacja OpenAPI,
- **SQLAlchemy async** - dostęp do danych,
- **PostgreSQL** - baza uruchamiana w Docker Compose,
- **Alembic** - wersjonowanie schematu,
- **Pydantic** - walidacja response,
- **httpx** - asynchroniczna komunikacja z Jolpica,
- **slowapi** - rate limiting.

## Roadmap

- frontend do wizualizacji statystyk i porównań,
- więcej filtrów dla sezonów i kierowców,
- testy integracyjne z mockowanym Jolpica API,
- monitoring i metryki API.

## Źródło danych

Dane historyczne są pobierane z [Jolpica F1 API](https://api.jolpi.ca/ergast/f1/), następcy Ergast Developer API. F1 Stats nie jest oficjalnym produktem Formula 1.
