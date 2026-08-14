from fastapi import FastAPI, HTTPException, Depends
import httpx
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select
from schemas import Driver, Race
from database import engine, Base, get_session
from models import Drivers, Races

app = FastAPI()

Base.metadata.create_all(engine)

@app.get("/")
async def root():
    return {"message": "Siema"}

@app.get("/drivers/{driver_id}", response_model=Driver)
async def get_driver(driver_id: str, session: Annotated[Session, Depends(get_session)]):
    stmt = select(Drivers).where(Drivers.driverId == driver_id)
    driverResult = session.execute(stmt).scalars().first()
    if driverResult != None:
        return driverResult
    else:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'https://api.jolpi.ca/ergast/f1/drivers/{driver_id}.json')
            if response.json()["MRData"]["DriverTable"]["Drivers"] == []:
                raise HTTPException(status_code=404, detail="Driver not found")
            data = response.json()["MRData"]["DriverTable"]["Drivers"][0]
            newDriver = Drivers(
                driverId=driver_id,
                name=data["givenName"],
                lastName=data["familyName"],
                driverNumber=data["permanentNumber"]
            )
            session.add(newDriver)
            session.commit()
            session.refresh(newDriver)
            return newDriver
        
@app.get("/drivers", response_model=list[Driver])
async def get_drivers(session: Annotated[Session, Depends(get_session)]):
    stmt = select(Drivers)
    driversResult = session.execute(stmt).scalars()
    return driversResult

@app.get("/races/{season}", response_model=list[Race])
async def get_races(season: str, session: Annotated[Session, Depends(get_session)]):
    stmt = select(Races).where(Races.season == season)
    racesResult = session.execute(stmt).scalars().all()
    if racesResult != []:
        return racesResult
    else:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'https://api.jolpi.ca/ergast/f1/{season}/races.json')
            data = response.json()["MRData"]["RaceTable"]["Races"]
            if response.json()["MRData"]["RaceTable"]["Races"] == []:
                raise HTTPException(status_code=404, detail="Races not found")
            for x in range(len(data)):
                newRace = Races(
                    season=season,
                    raceName=data[x]["raceName"],
                    date=data[x]["date"]
                )
                session.add(newRace)
            session.commit()
            
            return session.execute(stmt).scalars().all()