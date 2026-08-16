from sqlalchemy import String, Float
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
    nationality: Mapped[str] = mapped_column(String(30))
    winningPercentage: Mapped[float] = mapped_column(Float, server_default="0.0")


class Races(Base):
    __tablename__ = "race"

    id: Mapped[int] = mapped_column(primary_key=True)
    season: Mapped[str] = mapped_column(String(4))
    raceName: Mapped[str] = mapped_column(String(30))
    date: Mapped[str] = mapped_column(String(30))
    circuitName: Mapped[str] = mapped_column(String(50))
    locality: Mapped[str] = mapped_column(String(50))
    country: Mapped[str] = mapped_column(String(50))
    lenght: Mapped[str] = mapped_column(String(50))
