from typing import Optional

from sqlalchemy import String, Float, Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from database import Base


class Drivers(Base):
    __tablename__ = "driver"

    id: Mapped[int] = mapped_column(primary_key=True)
    driverId: Mapped[str] = mapped_column(String(30))
    name: Mapped[str] = mapped_column(String(30))
    lastName: Mapped[str] = mapped_column(String(30))
    driverNumber: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    nationality: Mapped[str] = mapped_column(String(30))
    winningPercentage: Mapped[float] = mapped_column(Float, server_default="0.0")
    hatTricks: Mapped[int] = mapped_column(Integer, server_default="0")
    poles: Mapped[int] = mapped_column(Integer, server_default="0")
    podiums: Mapped[int] = mapped_column(Integer, server_default="0")
    avgStartPosition: Mapped[float] = mapped_column(Float, server_default="0.0")
    avgEndPosition: Mapped[float] = mapped_column(Float, server_default="0.0")

class Races(Base):
    __tablename__ = "race"

    id: Mapped[int] = mapped_column(primary_key=True)
    season: Mapped[str] = mapped_column(String(4))
    raceName: Mapped[str] = mapped_column(String(30))
    date: Mapped[str] = mapped_column(String(30))
    circuitName: Mapped[str] = mapped_column(String(50))
    locality: Mapped[str] = mapped_column(String(50))
    country: Mapped[str] = mapped_column(String(50))
