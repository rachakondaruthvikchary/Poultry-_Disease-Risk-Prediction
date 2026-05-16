#!/usr/bin/env python3
"""
Direct Database User Creation Script
Creates a test user directly in the database without needing the API running
"""

import sys
import os

# Add Backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.user import User
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(email: str, password: str, full_name: str):
    """Create a user in the database"""
    db = SessionLocal()
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"❌ User already exists: {email}")
            return False
        
        # Hash password
        hashed_password = pwd_context.hash(password)
        
        # Create new user
        new_user = User(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password
        )
        
        db.add(new_user)
        db.commit()
        
        print("✅ User created successfully!")
        print(f"   Email: {email}")
        print(f"   Name: {full_name}")
        print(f"   Password: {password}")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating user: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🐔 PoultryGuard AI - Create Test User")
    print("=" * 50)
    
    # Create test user
    success = create_user(
        email="test@test.com",
        password="test1234",
        full_name="Test User"
    )
    
    if success:
        print("\n✅ Test user is ready!")
        print("   Login with: test@test.com / test1234")
    else:
        print("\n❌ Failed to create user")
        sys.exit(1)
