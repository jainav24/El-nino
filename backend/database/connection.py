from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.config import DATABASE_URL
from backend.database.models import Base


# Create SQLAlchemy engine
# check_same_thread=False is required only for SQLite
connect_args = (
    {"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)

# Create database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def init_db():
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency to get a database session."""
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()