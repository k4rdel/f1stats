from pydantic import BaseModel

class Driver(BaseModel):
    driverId: str
    name: str
    lastName: str
    driverNumber: str
    
class Race(BaseModel):
    season: str
    raceName: str
    date: str
    circuitName: str