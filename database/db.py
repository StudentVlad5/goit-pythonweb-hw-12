"""
Database Module
---------------
This module handles the SQLAlchemy engine initialization, session management, 
and database schema creation.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.config import settings
from database.models import Base

engine = create_engine(settings.sqlalchemy_database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency provider for database sessions.
    
    Yields a database session to be used in FastAPI dependencies. 
    Ensures the session is closed after the request is finished.

    :yields: SQLAlchemy Session object.
    :rtype: Generator[Session, None, None]
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функція для створення всіх таблиць у БД
def init_db():
    """
    Initializes the database by creating all defined tables.
    
    This function uses the SQLAlchemy Base metadata to generate the schema 
    in the database connected via the current engine.
    
    :return: None
    """
    Base.metadata.create_all(bind=engine)