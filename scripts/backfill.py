import os
import time
import httpx
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import select, create_engine
from app.models import Drivers, Races
from dotenv import load_dotenv
from app.utils import *

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL_LOCAL") or os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    echo=True,
)

async def fetch_all_stats(driver_id):
    avgPositions, winPct, hatTricks, poles, podiums = await asyncio.gather(
        averagePositions(driver_id),
        winning_percentage(driver_id),
        howManyHatTricks(driver_id),
        howManyPoles(driver_id),
        howManyPodiums(driver_id),
    )
    return avgPositions, winPct, hatTricks, poles, podiums

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
            if driver.winningPercentage == 0.0 or driver.hatTricks == 0 or driver.poles == 0 or driver.podiums == 0 or driver.avgStartPosition == 0.0 or driver.avgEndPosition == 0.0:
                (avgStart, avgEnd), winPct, hatTricks, poles, podiums = asyncio.run(fetch_all_stats(driver.driverId))
                driver.winningPercentage = winPct
                driver.hatTricks = hatTricks
                driver.poles = poles
                driver.podiums = podiums
                driver.avgStartPosition = avgStart
                driver.avgEndPosition = avgEnd
                time.sleep(1)
    session.commit()