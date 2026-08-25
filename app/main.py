import asyncio
import httpx

from fastapi import FastAPI, HTTPException, Depends, Request
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .schemas import Driver, Race, Comparison
from .database import get_session, get_engine
from .models import Drivers, Races
from .utils import *

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/")
@limiter.limit("15/minute")
async def root(request: Request):
    return {"message": "Siema"}


async def fetch_or_get_driver(driver_id, session):
    stmt = select(Drivers).where(Drivers.driverId == driver_id)
    driverResult = (await session.execute(stmt)).scalars().first()
    if driverResult is not None:
        return driverResult
    else:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.jolpi.ca/ergast/f1/drivers/{driver_id}.json"
            )
            if response.json()["MRData"]["DriverTable"]["Drivers"] == []:
                raise HTTPException(status_code=404, detail="Driver not found")
            data = response.json()["MRData"]["DriverTable"]["Drivers"][0]
            
            avgStartPosition, avgEndPosition = await averagePositions(driver_id)
            
            winPct, hatTricks, poles, podiums = await asyncio.gather(
                winning_percentage(driver_id),
                howManyHatTricks(driver_id),
                howManyPoles(driver_id),
                howManyPodiums(driver_id)
            )
            
            newDriver = Drivers(
                driverId = driver_id,
                name = data["givenName"],
                lastName = data["familyName"],
                driverNumber = data.get("permanentNumber", None),
                nationality = data["nationality"],
                winningPercentage = winPct,
                hatTricks = hatTricks,
                poles = poles,
                podiums = podiums,
                avgStartPosition = avgStartPosition,
                avgEndPosition = avgEndPosition
            )
            session.add(newDriver)
            await session.commit()
            await session.refresh(newDriver)
            return newDriver

async def fetch_or_get_driver_isolated(driver_id, engine):
    async with AsyncSession(engine) as session:
        return await fetch_or_get_driver(driver_id, session)

@app.get("/drivers/{driver_id}", response_model=Driver)
@limiter.limit("10/minute")
async def get_driver(driver_id: str, session: Annotated[AsyncSession, Depends(get_session)], request: Request):
    return await fetch_or_get_driver(driver_id, session)


@app.get("/drivers", response_model=list[Driver])
@limiter.limit("15/minute")
async def get_drivers(session: Annotated[AsyncSession, Depends(get_session)], request: Request):
    stmt = select(Drivers)
    driversResult = (await session.execute(stmt)).scalars().all()
    if driversResult != []:
        return driversResult
    else:
        raise HTTPException(status_code=404, detail="Races not found")

@app.get("/races/{season}", response_model=list[Race])
@limiter.limit("15/minute")
async def get_races(season: str, session: Annotated[AsyncSession, Depends(get_session)], request: Request):
    stmt = select(Races).where(Races.season == season)
    racesResult = (await session.execute(stmt)).scalars().all()
    if racesResult != []:
        return racesResult
    else:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.jolpi.ca/ergast/f1/{season}/races.json"
            )
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="Season not found")
            data = response.json()["MRData"]["RaceTable"]["Races"]
            if data == []:
                raise HTTPException(status_code=404, detail="Races not found")
            for x in range(len(data)):
                newRace = Races(
                    season=season,
                    raceName=data[x]["raceName"],
                    date=data[x]["date"],
                    circuitName=data[x]["Circuit"]["circuitName"],
                    locality = data[x]["Circuit"]["Location"]["locality"],
                    country = data[x]["Circuit"]["Location"]["country"]
            )
                session.add(newRace)
            await session.commit()

            return (await session.execute(stmt)).scalars().all()

@app.get("/compare/{driver1}/{driver2}", response_model=Comparison)
@limiter.limit("10/minute")
async def compare_driver(driver1: str, driver2: str, engine: Annotated[AsyncSession, Depends(get_engine)], request: Request):
    result1, result2 = await asyncio.gather(
        fetch_or_get_driver_isolated(driver1, engine),
        fetch_or_get_driver_isolated(driver2, engine)
    )
    return Comparison(driver1=result1, driver2=result2)

@app.get("/health")
@limiter.limit("15/minute")
async def health_check(session: Annotated[AsyncSession, Depends(get_session)], request: Request):
    try:
        await session.execute(text('SELECT 1'))
    except Exception as e:
        print(f"!!! Health check error: {e}")
        raise HTTPException(status_code=503, detail="Database is unavailable")
    return {"status": "ok", "database": "connected"}