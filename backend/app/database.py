# SQLAlchemy is a Python library for working with relational databases (PostgreSQL, MySQL, SQLite, etc.). The name is a blend of “SQL” and “alchemy,” as in transforming one thing into another: it turns database tables and rows into Python objects and back.

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./z_sentinel.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)