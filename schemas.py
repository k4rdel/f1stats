from pydantic import BaseModel, ConfigDict

class Driver(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    driverId: str
    name: str
    lastName: str
    driverNumber: str
    
class Race(BaseModel):
    season: str
    raceName: str
    date: str
    circuitName: str
    
class Comparison(BaseModel):
    driver1: Driver
    driver2: Driver