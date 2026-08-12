from fastapi import FastAPI, HTTPException
import httpx
from pydantic import BaseModel

class Driver(BaseModel):
    givenName: str
    familyName: str
    permanentNumber: str

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Siema"}

@app.get("/drivers/{driver_id}", response_model=Driver)
async def get_driver(driver_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f'https://api.jolpi.ca/ergast/f1/drivers/{driver_id}.json')
        if response.json()["MRData"]["DriverTable"]["Drivers"] == []:
            raise HTTPException(status_code=404, detail="Driver not found")
        return response.json()["MRData"]["DriverTable"]["Drivers"][0]