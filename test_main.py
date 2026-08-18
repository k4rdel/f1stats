import os
import pytest
import asyncio

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///test_database.db")

from fastapi.testclient import TestClient
from main import app
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from database import get_session, Base
from models import Drivers, Races

client = TestClient(app)


async def make_test_engine():
    if os.path.exists("test_database.db"):
        os.remove("test_database.db")
    newEngine = create_async_engine("sqlite+aiosqlite:///test_database.db", echo=True)
    async with newEngine.begin() as conn: 
        await conn.run_sync(Base.metadata.create_all)
    return newEngine


test_engine = asyncio.run(make_test_engine())


async def override_dependency():
    async with AsyncSession(test_engine) as session:
        yield session


app.dependency_overrides[get_session] = override_dependency


@pytest.fixture(autouse=True)
async def clear_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Siema"}


async def test_get_driver_from_cache():
    async with AsyncSession(test_engine) as session:
        newDriver = Drivers(
            driverId="leclerc", name="Charles", lastName="Leclerc", driverNumber="16", nationality = "Monegasque", winningPercentage = 98.12, hatTricks = 10, poles = 4, podiums = 2, avgStartPosition = 2.31, avgEndPosition = 1.24
        )
        session.add(newDriver)
        await session.commit()
    response = client.get("/drivers/leclerc")
    assert response.status_code == 200
    assert response.json() == {
        "driverId": "leclerc",
        "name": "Charles",
        "lastName": "Leclerc",
        "driverNumber": "16",
        "nationality": "Monegasque",
        "winningPercentage": 98.12,
        "hatTricks": 10,
        "poles": 4,
        "podiums": 2,
        "avgStartPosition": 2.31,
        "avgEndPosition": 1.24
    }

async def test_get_races_from_cache():
    async with AsyncSession(test_engine) as session:
        newRace = Races(
            season="2024", raceName="Bahrain Grand Prix", date="2024-03-02", circuitName="Bahrain International Circuit", locality = "Sakhir", country = "Bahrain", lenght = "50.5106"
        )
        session.add(newRace)
        await session.commit()
    response = client.get("/races/2024")
    assert response.status_code == 200
    assert response.json() == [{
        "season": "2024", 
        "raceName": "Bahrain Grand Prix", 
        "date": "2024-03-02", 
        "circuitName": "Bahrain International Circuit", 
        "locality": "Sakhir", 
        "country": "Bahrain", 
        "lenght": "50.5106"
    }]