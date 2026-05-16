"""
Add 14 days of sample data to show chart trends
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.farm import Farm
from app.models.daily_record import DailyRecord

def add_sample_data():
    """Add 14 days of sample daily records"""
    db = SessionLocal()
    
    try:
        # Get the first user
        user = db.query(User).first()
        if not user:
            print("❌ No users found. Please create a user first!")
            return
        
        print(f"📝 Using user: {user.email}")
        
        # Get or create a farm
        farm = db.query(Farm).filter(Farm.user_id == user.id).first()
        if not farm:
            farm = Farm(
                user_id=user.id,
                name="Sample Farm",
                location="Sample Location",
                flock_size=1000
            )
            db.add(farm)
            db.commit()
            print(f"✅ Created farm: {farm.name}")
        else:
            print(f"📍 Using farm: {farm.name}")
        
        # Add 14 days of sample data
        start_date = datetime.now().date() - timedelta(days=14)
        
        risk_scores = [
            15, 18, 22, 25, 28, 32, 35, 38, 40, 38, 35, 30, 25, 20
        ]
        
        risk_categories = {
            score: "Low" if score < 30 else ("Medium" if score < 70 else "High")
            for score in risk_scores
        }
        
        for i, risk_score in enumerate(risk_scores):
            record_date = start_date + timedelta(days=i)
            
            # Check if record already exists
            existing = db.query(DailyRecord).filter(
                DailyRecord.farm_id == farm.id,
                DailyRecord.record_date == record_date
            ).first()
            
            if existing:
                print(f"⏭️  Skipping {record_date} (already exists)")
                continue
            
            record = DailyRecord(
                farm_id=farm.id,
                record_date=record_date,
                temperature=22.5 + (i * 0.3),
                humidity=65.0 + (i * 0.5),
                feed_intake=80 - (i * 1.5),
                water_intake=120 - (i * 1),
                activity_level=75 - (i * 1.2),
                mortality_rate=0.5 + (i * 0.08),
                bird_age=20 + i,
                risk_score=risk_score,
                risk_category=risk_categories[risk_score]
            )
            db.add(record)
            db.commit()
            print(f"✅ Added data for {record_date} - Risk: {risk_score} ({risk_categories[risk_score]})")
        
        print("\n🎉 Sample data added successfully!")
        print("📊 Go to Dashboard to see the Risk Trend chart!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_sample_data()
