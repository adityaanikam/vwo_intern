"""
Database configuration and session management
Supports both SQLite and PostgreSQL
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from models import Base
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blood_test_analyser.db")

# Create engine based on database type
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False  # Set to True for SQL query logging
    )
else:
    # PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database with tables"""
    create_tables()
    print("Database initialized successfully!")

# Database utilities
def get_analysis_by_id(db: Session, analysis_id: str):
    """Get analysis by ID"""
    from models import BloodTestAnalysis
    return db.query(BloodTestAnalysis).filter(BloodTestAnalysis.analysis_id == analysis_id).first()

def get_user_by_id(db: Session, user_id: str):
    """Get user by ID"""
    from models import User
    return db.query(User).filter(User.user_id == user_id).first()

def create_user(db: Session, email: str = None, name: str = None):
    """Create a new user"""
    from models import User
    user = User(email=email, name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_analysis(db: Session, original_filename: str, file_path: str, query: str, user_id: str = None):
    """Create a new analysis record"""
    from models import BloodTestAnalysis
    analysis = BloodTestAnalysis(
        original_filename=original_filename,
        file_path=file_path,
        query=query,
        user_id=user_id
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis

def update_analysis_status(db: Session, analysis_id: str, status: str, progress: float = None, error_message: str = None):
    """Update analysis status and progress"""
    from models import BloodTestAnalysis
    from datetime import datetime
    
    analysis = get_analysis_by_id(db, analysis_id)
    if analysis:
        analysis.status = status
        if progress is not None:
            analysis.progress = progress
        if error_message:
            analysis.error_message = error_message
        
        if status == "processing" and not analysis.started_at:
            analysis.started_at = datetime.utcnow()
        elif status in ["completed", "failed"] and not analysis.completed_at:
            analysis.completed_at = datetime.utcnow()
        
        db.commit()
        return analysis
    return None

def update_analysis_result(db: Session, analysis_id: str, agent_type: str, result: str):
    """Update analysis result for a specific agent"""
    from models import BloodTestAnalysis
    
    analysis = get_analysis_by_id(db, analysis_id)
    if analysis:
        if agent_type == "doctor":
            analysis.doctor_analysis = result
        elif agent_type == "verifier":
            analysis.verifier_analysis = result
        elif agent_type == "nutritionist":
            analysis.nutritionist_analysis = result
        elif agent_type == "exercise":
            analysis.exercise_analysis = result
        
        db.commit()
        return analysis
    return None 