from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

engine = create_engine("sqlite:///database.db", echo=True)

class Base(DeclarativeBase):
    pass

def get_session():
    with Session(engine) as session:
        yield session