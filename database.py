import os
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(
    DATABASE_URL.replace("postgresql+psycopg", "postgresql+asyncpg"),
    echo=True,
)

class Base(DeclarativeBase):
    pass


async def get_session():
    async with AsyncSession(engine) as session:
        yield session

def get_engine():
    return engine