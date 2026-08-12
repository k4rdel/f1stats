from pydantic import BaseModel

class Driver(BaseModel):
    driverId: str
    name: str
    lastName: str
    driverNumber: str