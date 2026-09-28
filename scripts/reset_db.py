import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.database.connection import engine
from backend.database.models import Base

if __name__ == "__main__":
    print("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully.")
