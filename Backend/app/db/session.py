from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine_kwargs = {"pool_pre_ping": True}
if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Ensure tables are created on module load for serverless environments
from app.models.base import Base
# Import all models so they are registered with Base.metadata
from app.models.user import User
# Using try-except for others to prevent circular imports if they exist
try:
    from app.models.farm import Farm
    from app.models.record import Record
except ImportError:
    pass

Base.metadata.create_all(bind=engine)
