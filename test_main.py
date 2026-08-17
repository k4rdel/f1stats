import os
import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:///test_database.db")

from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from database import get_session, Base
from models import Drivers, Races

client = TestClient(app)


def make_test_engine():
    if os.path.exists("test_database.db"):
        os.remove("test_database.db")
    newEngine = create_engine("sqlite:///test_database.db", echo=True)
    Base.metadata.create_all(newEngine)
    return newEngine


test_engine = make_test_engine()


def override_dependency():
    with Session(test_engine) as session:
        yield session


app.dependency_overrides[get_session] = override_dependency


@pytest.fixture(autouse=True)
def clear_database():
    Base.metadata.drop_all(test_engine)
    Base.metadata.create_all(test_engine)
    yield


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Siema"}


def test_get_driver_from_cache():
    with Session(test_engine) as session:
        newDriver = Drivers(
            driverId="leclerc", name="Charles", lastName="Leclerc", driverNumber="16", nationality = "Monegasque", winningPercentage = 98.12, hatTricks = 10, poles = 4, podiums = 2, avgStartPosition = 2.31, avgEndPosition = 1.24
        )
        session.add(newDriver)
        session.commit()
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

def test_get_races_from_cache():
    with Session(test_engine) as session:
        newRace = Races(
            season="2024", raceName="Bahrain Grand Prix", date="2024-03-02", circuitName="Bahrain International Circuit", locality = "Sakhir", country = "Bahrain", lenght = "50.5106"
        )
        session.add(newRace)
        session.commit()
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