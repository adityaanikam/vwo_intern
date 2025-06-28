#!/usr/bin/env python3
"""
Database initialization script
Creates all tables and sets up the database
"""

import os
import sys
from database import init_db, engine
from models import Base

def main():
    """Initialize the database"""
    print("🗄️  Initializing Blood Test Analyser Database...")
    
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # Initialize database
        init_db()
        
        print("🎉 Database initialization completed!")
        print("\n📋 Database Configuration:")
        print(f"   Database URL: {os.getenv('DATABASE_URL', 'sqlite:///./blood_test_analyser.db')}")
        print(f"   Tables created: users, blood_test_analyses, analysis_tasks")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 