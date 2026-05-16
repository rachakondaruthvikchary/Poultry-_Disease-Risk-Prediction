"""
Database Initialization Script for PoultryGuard AI
Run this to create all database tables
"""

from app.db.session import engine
from app.models.base import Base

# Import all models to ensure they're registered with Base
from app.models.user import User
from app.models.farm import Farm
from app.models.daily_record import DailyRecord
from app.models.image_prediction import ImagePrediction
from app.models.alert import Alert


def init_db():
    """Initialize database with all tables"""
    print("🐔 PoultryGuard AI - Database Initialization")
    print("=" * 60)
    
    print("\n📊 Creating all tables...")
    Base.metadata.create_all(bind=engine)
    
    print("\n✅ Database initialized successfully!")
    print("\nCreated tables:")
    for table_name in Base.metadata.tables.keys():
        print(f"  ✓ {table_name}")
    
    print("\n🚀 Database is ready!")


if __name__ == "__main__":
    init_db()
