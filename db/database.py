from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Load database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db/real_estate")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Function to initialize the database
def init_db():
    from db.models import Base  # Import models to register them
    Base.metadata.create_all(engine)  # Create tables if they don't exist
    print("Database initialized.")

def check_link_exists():
    pass

def save_new_listing():
    pass

def save_new_property():
    pass
