"""
Database Initialization Script for PoultryGuard AI

This script creates all necessary tables with proper schema, indexes, and foreign keys.
Run this before starting the FastAPI server.
"""

from sqlalchemy import create_engine
from app.models.base import Base
from app.db.base import *  # Import all models
from app.core.config import settings

def init_db():
    """Initialize database with all tables"""
    print("🐔 PoultryGuard AI - Database Initialization")
    print("=" * 60)
    print(f"Database URL: {settings.DATABASE_URL.split('@')[-1]}")
    
    engine = create_engine(settings.DATABASE_URL, echo=True)
    
    print("\n📊 Creating all tables...")
    Base.metadata.create_all(bind=engine)
    
    print("\n✅ Database initialized successfully!")
    print("\nCreated tables:")
    for table_name in Base.metadata.tables.keys():
        print(f"  ✓ {table_name}")
    
    print("\n🚀 Ready to start the API server!")


if __name__ == "__main__":
    init_db()
