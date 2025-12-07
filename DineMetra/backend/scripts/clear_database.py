"""Clear all data from database"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.database.database import SessionLocal, engine
from app.models.database_models import Base

print("⚠️  Clearing all data from database...")
response = input("This will delete ALL data. Continue? (yes/no): ")

if response.lower() != 'yes':
    print("Cancelled.")
    exit(0)

# Drop all tables
Base.metadata.drop_all(bind=engine)
print("✓ Tables dropped")

# Recreate them
Base.metadata.create_all(bind=engine)
print("✓ Tables recreated")
print("✅ Database is now empty and ready for migration!")
