from fastapi import FastAPI, HTTPException, Depends
import httpx
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select
from schemas import Driver 
from database import engine, Base, get_session
from models import Drivers

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