from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from database import get_session, Base
from models import Drivers

client = TestClient(app)


def make_test_engine():
    newEngine = create_engine("sqlite:///test_database.db", echo=True)
    Base.metadata.create_all(newEngine)
    return newEngine


def override_dependency():
    newEngine = make_test_engine()
    with Session(newEngine) as session:
        yield session


app.dependency_overrides[get_session] = override_dependency


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Siema"}


def test_get_driver_from_cache():
    with Session(make_test_engine()) as session:
        newDriver = Drivers(
            driverId="leclerc", name="Charles", lastName="Leclerc", driverNumber="16"
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
        "nationality": None
    }
