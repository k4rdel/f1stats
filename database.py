from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

engine = create_engine("postgresql+psycopg://oskar:admin1234@db:5432/f1stats", echo=True)

class Base(DeclarativeBase):
    pass

def get_session():
    with Session(engine) as session:
        yield session