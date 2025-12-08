#!/usr/bin/env python
"""Test database connection"""

from app.database.database import check_db_connection, init_db, engine, SessionLocal
from sqlalchemy import text

print("🔍 Testing Neon Database Connection")
print("=" * 60)

# Check if engine exists
if engine:
    print("✓ Database engine created")
    print(f"  URL: {engine.url}")
else:
    print("❌ No database engine")
    exit(1)

# Test connection
print("\nTesting connection...")
if check_db_connection():
    print("✅ Connection successful!")
else:
    print("❌ Connection failed")
    exit(1)

# Try a simple query
print("\nTesting query execution...")
try:
    db = SessionLocal()
    result = db.execute(text("SELECT version()"))
    version = result.scalar()
    print(f"✓ PostgreSQL version: {version[:50]}...")
    db.close()
    print("✅ Query successful!")
except Exception as e:
    print(f"❌ Query failed: {e}")
    exit(1)

# Initialize tables
print("\nInitializing database tables...")
try:
    init_db()
    print("✅ Tables initialized!")
except Exception as e:
    print(f"❌ Table creation failed: {e}")
    exit(1)

print("\n" + "=" * 60)
print("🎉 ALL TESTS PASSED - Database ready for migration!")
print("=" * 60)
