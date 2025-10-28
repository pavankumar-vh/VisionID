"""
User Model - Database schema for registered users
Stores user information and face embeddings
"""

from sqlalchemy import Column, String, DateTime, LargeBinary, Integer
from sqlalchemy.sql import func
from app.models.database import Base


class User(Base):
    """
    User model for storing registered users and their face embeddings
    """
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    embedding = Column(LargeBinary, nullable=False)  # Stores numpy array as bytes
    image_path = Column(String, nullable=True)
    metadata = Column(String, nullable=True)  # JSON string for additional info
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<User(id={self.id}, name={self.name})>"


class AttendanceLog(Base):
    """
    Attendance log model for tracking attendance records
    """
    __tablename__ = "attendance_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    user_name = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    status = Column(String, default="present")  # present, absent, late
    confidence = Column(String, nullable=True)  # Recognition confidence score
    image_path = Column(String, nullable=True)  # Path to attendance image
    
    def __repr__(self):
        return f"<AttendanceLog(id={self.id}, user={self.user_name}, time={self.timestamp})>"


class RecognitionHistory(Base):
    """
    Recognition history model for tracking all recognition attempts
    """
    __tablename__ = "recognition_history"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, nullable=True, index=True)  # Null if unknown face
    user_name = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    confidence = Column(String, nullable=True)
    recognized = Column(String, default="false")  # "true" or "false"
    image_path = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<RecognitionHistory(id={self.id}, user={self.user_name}, recognized={self.recognized})>"
