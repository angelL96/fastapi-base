from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, create_engine, select

from app.core.config import settings


if settings.SQLALCHEMY_DATABASE_URI and settings.SQLALCHEMY_DATABASE_URI.startswith("postgresql"):
    # PostgreSQL connection
    connect_args = {"check_same_thread": False}
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
else:
    # SQLite fallback
    sqlite_file_name = "database.db"
    sqlite_url = f"sqlite:///{sqlite_file_name}"
    connect_args = {"check_same_thread": False}
    engine = create_engine(sqlite_url, connect_args=connect_args)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]