from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from database import Base

class Drivers(Base):
    __tablename__ = "driver"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    driverId: Mapped[str] = mapped_column(String(30))
    name: Mapped[str] = mapped_column(String(30))
    lastName: Mapped[str] = mapped_column(String(30))
    driverNumber: Mapped[str] = mapped_column(String(10))
    
    def __repr__(self) -> str:
        return f"Driver(id={self.id!r}), driverId={self.driverId!r}), name={self.name!r}, lastName={self.lastName!r}, driverNumber={self.driverNumber!r}"