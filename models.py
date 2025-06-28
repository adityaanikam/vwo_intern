"""
Database models for Blood Test Analyser
Handles storage of analysis results and user metadata
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    """User model for storing user metadata"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=True)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to analysis results
    analyses = relationship("BloodTestAnalysis", back_populates="user")

class BloodTestAnalysis(Base):
    """Blood test analysis results model"""
    __tablename__ = "blood_test_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), index=True, nullable=True)  # Can be anonymous
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    query = Column(Text, nullable=False)
    
    # Analysis results from different agents
    doctor_analysis = Column(Text, nullable=True)
    verifier_analysis = Column(Text, nullable=True)
    nutritionist_analysis = Column(Text, nullable=True)
    exercise_analysis = Column(Text, nullable=True)
    
    # Processing status
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    progress = Column(Float, default=0.0)  # 0.0 to 1.0
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to user
    user = relationship("User", back_populates="analyses")

class AnalysisTask(Base):
    """Celery task tracking model"""
    __tablename__ = "analysis_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(255), unique=True, index=True, nullable=False)
    analysis_id = Column(String(36), index=True, nullable=False)
    task_type = Column(String(50), nullable=False)  # doctor, verifier, nutritionist, exercise
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    result = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

# Import relationship after Base is defined
from sqlalchemy.orm import relationship 