"""
CRUD Operations - Database operations for users and attendance
"""

from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.models.user import User, AttendanceLog, RecognitionHistory
from typing import List, Optional
from datetime import datetime, date
import uuid


# ============= USER OPERATIONS =============

def create_user(db: Session, name: str, embedding: bytes, image_path: str = None, metadata: str = None) -> User:
    """
    Create a new user in the database
    
    Args:
        db: Database session
        name: User's name
        embedding: Face embedding as bytes
        image_path: Path to user's image
        metadata: Additional metadata as JSON string
        
    Returns:
        Created User object
    """
    user_id = str(uuid.uuid4())
    db_user = User(
        id=user_id,
        name=name,
        embedding=embedding,
        image_path=image_path,
        metadata=metadata
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: str) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_name(db: Session, name: str) -> Optional[User]:
    """Get user by name"""
    return db.query(User).filter(User.name == name).first()


def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get all users with pagination"""
    return db.query(User).offset(skip).limit(limit).all()


def get_all_embeddings(db: Session) -> List[tuple]:
    """
    Get all user embeddings for matching
    
    Returns:
        List of (user_id, embedding_bytes) tuples
    """
    users = db.query(User.id, User.embedding).all()
    return [(user.id, user.embedding) for user in users]


def update_user(db: Session, user_id: str, name: str = None, embedding: bytes = None) -> Optional[User]:
    """Update user information"""
    db_user = get_user(db, user_id)
    if db_user:
        if name:
            db_user.name = name
        if embedding:
            db_user.embedding = embedding
        db.commit()
        db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: str) -> bool:
    """Delete a user"""
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False


# ============= ATTENDANCE OPERATIONS =============

def create_attendance_log(
    db: Session, 
    user_id: str, 
    user_name: str, 
    status: str = "present",
    confidence: str = None,
    image_path: str = None
) -> AttendanceLog:
    """Create an attendance log entry"""
    log = AttendanceLog(
        user_id=user_id,
        user_name=user_name,
        status=status,
        confidence=confidence,
        image_path=image_path
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_today_attendance(db: Session) -> List[AttendanceLog]:
    """Get today's attendance records"""
    today = date.today()
    return db.query(AttendanceLog).filter(
        func.date(AttendanceLog.timestamp) == today
    ).all()


def get_attendance_by_date_range(
    db: Session, 
    start_date: date, 
    end_date: date,
    user_id: str = None
) -> List[AttendanceLog]:
    """Get attendance records for a date range"""
    query = db.query(AttendanceLog).filter(
        AttendanceLog.timestamp >= start_date,
        AttendanceLog.timestamp <= end_date
    )
    if user_id:
        query = query.filter(AttendanceLog.user_id == user_id)
    return query.all()


def get_user_attendance(db: Session, user_id: str, limit: int = 30) -> List[AttendanceLog]:
    """Get attendance history for a specific user"""
    return db.query(AttendanceLog).filter(
        AttendanceLog.user_id == user_id
    ).order_by(AttendanceLog.timestamp.desc()).limit(limit).all()


# ============= RECOGNITION HISTORY OPERATIONS =============

def create_recognition_record(
    db: Session,
    user_id: str = None,
    user_name: str = None,
    confidence: str = None,
    recognized: str = "false",
    image_path: str = None
) -> RecognitionHistory:
    """Create a recognition history record"""
    record = RecognitionHistory(
        user_id=user_id,
        user_name=user_name,
        confidence=confidence,
        recognized=recognized,
        image_path=image_path
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_recognition_history(db: Session, limit: int = 50) -> List[RecognitionHistory]:
    """Get recent recognition history"""
    return db.query(RecognitionHistory).order_by(
        RecognitionHistory.timestamp.desc()
    ).limit(limit).all()


def get_user_recognition_history(db: Session, user_id: str, limit: int = 50) -> List[RecognitionHistory]:
    """Get recognition history for a specific user"""
    return db.query(RecognitionHistory).filter(
        RecognitionHistory.user_id == user_id
    ).order_by(RecognitionHistory.timestamp.desc()).limit(limit).all()
