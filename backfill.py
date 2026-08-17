import os
import httpx
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import select, create_engine
from models import Drivers, Races
from dotenv import load_dotenv
from utils import *

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL_LOCAL") or os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    echo=True,
)

with Session(engine) as session:
    stmt = select(Drivers)
    driversResult = session.execute(stmt).scalars().all()
    if driversResult == []:
        print("No drivers avaliable")
    else:
        for driver in driversResult:
            if driver.nationality is None:
                with httpx.Client() as client:
                    response = client.get(f"https://api.jolpi.ca/ergast/f1/drivers/{driver.driverId}.json")
                    data = response.json()["MRData"]["DriverTable"]["Drivers"][0]
                    driver.nationality = data["nationality"]
            if driver.winningPercentage == 0.0:
                driver.winningPercentage = asyncio.run(winning_percentage(driver.driverId))
            if driver.hatTricks == 0:
                driver.hatTricks = asyncio.run(howManyHatTricks(driver.driverId))
    session.commit()