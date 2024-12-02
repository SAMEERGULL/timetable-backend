# database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Database configuration
DATABASE_URL = 'postgresql://postgres:1234@localhost:5432/timetable' # Change this to your desired database URL

# Create the database engine
engine = create_engine(DATABASE_URL)

# Create all tables in the database (this creates tables based on the models defined in models.py)
Base.metadata.create_all(engine)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()