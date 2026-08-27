import os
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

raw_url = DATABASE_URL.replace("postgresql+psycopg", "postgresql+asyncpg")
needs_ssl = "sslmode=require" in raw_url

engine = create_async_engine(
    raw_url.split("?")[0],
    connect_args={"ssl": "require"} if needs_ssl else {},
    echo=True,
)

class Base(DeclarativeBase):
    pass


async def get_session():
    async with AsyncSession(engine) as session:
        yield session

def get_engine():
    return engine