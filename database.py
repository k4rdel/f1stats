import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    echo=True,
)


class Base(DeclarativeBase):
    pass


def get_session():
    with Session(engine) as session:
        yield session
