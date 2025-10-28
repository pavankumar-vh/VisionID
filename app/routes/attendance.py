"""
Attendance Routes - Attendance Tracking & Reporting Endpoints
"""

from fastapi import APIRouter, File, UploadFile, Query, HTTPException, Depends
from typing import Optional, List
from datetime import datetime, date, timedelta
from pydantic import BaseModel
from sqlalchemy.orm import Session
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.services.detector import FaceDetector
from app.services.embedder import FaceEmbedder
from app.services.matcher import FaceMatcher
from app.models.database import get_db
from app.models import crud
from app.utils.image_utils import read_image_file, validate_image
from app.utils.logger import log_attendance, log_error

router = APIRouter()

# Initialize services (cached)
face_detector = None
face_embedder = None
face_matcher = None
executor = ThreadPoolExecutor(max_workers=4)


def get_services():
    """Get or initialize face recognition services"""
    global face_detector, face_embedder, face_matcher
    if face_detector is None:
        face_detector = FaceDetector(ctx_id=0)
    if face_embedder is None:
        face_embedder = FaceEmbedder(ctx_id=0)
    if face_matcher is None:
        face_matcher = FaceMatcher(similarity_threshold=0.6)
    return face_detector, face_embedder, face_matcher


class AttendanceRecord(BaseModel):
    """Model for attendance record"""
    user_id: str
    name: str
    timestamp: datetime
    status: str
    confidence: float


class AttendanceResponse(BaseModel):
    """Response model for attendance marking"""
    success: bool
    records: List[AttendanceRecord]
    message: str


@router.post("/attendance/mark", response_model=AttendanceResponse)
async def mark_attendance(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Mark attendance by recognizing faces in uploaded image
    
    Args:
        file: Image file containing faces for attendance
        db: Database session
        
    Returns:
        AttendanceResponse with marked attendance records
    """
    try:
        # Read and validate image
        image_bytes = await file.read()
        is_valid, error_msg = validate_image(image_bytes)
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        image = read_image_file(image_bytes)
        if image is None:
            raise HTTPException(status_code=400, detail="Failed to read image")
        
        # Get services
        detector, embedder, matcher = get_services()
        
        # Detect faces
        detected_faces = detector.detect_faces(image, threshold=0.5)
        
        if len(detected_faces) == 0:
            return AttendanceResponse(
                success=True,
                records=[],
                message="No faces detected in the image"
            )
        
        # Get known embeddings
        db_embeddings_data = crud.get_all_embeddings(db)
        known_embeddings = []
        
        for user_id, emb_bytes in db_embeddings_data:
            emb_array = embedder.bytes_to_embedding(emb_bytes)
            known_embeddings.append((user_id, emb_array))
        
        # Process faces
        attendance_records = []
        processed_users = set()  # Avoid duplicate attendance
        
        async def process_face(face_data):
            face_obj = face_data['face_obj']
            confidence = face_data['confidence']
            
            # Get embedding
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                executor,
                embedder.get_embedding,
                face_obj
            )
            
            if embedding is None:
                return None
            
            # Match
            if len(known_embeddings) > 0:
                match_result = await loop.run_in_executor(
                    executor,
                    matcher.match_embedding,
                    embedding,
                    known_embeddings,
                    0.6
                )
                
                if match_result:
                    user_id, similarity = match_result
                    
                    # Avoid duplicate attendance for same person
                    if user_id in processed_users:
                        return None
                    
                    user = crud.get_user(db, user_id)
                    
                    if user:
                        # Mark attendance in database
                        attendance_log = crud.create_attendance_log(
                            db=db,
                            user_id=user_id,
                            user_name=user.name,
                            status="present",
                            confidence=str(similarity)
                        )
                        
                        log_attendance(user_id, user.name, "present")
                        processed_users.add(user_id)
                        
                        return AttendanceRecord(
                            user_id=user_id,
                            name=user.name,
                            timestamp=attendance_log.timestamp,
                            status="present",
                            confidence=similarity
                        )
            
            return None
        
        # Process all faces
        results = await asyncio.gather(*[process_face(face) for face in detected_faces])
        attendance_records = [r for r in results if r is not None]
        
        return AttendanceResponse(
            success=True,
            records=attendance_records,
            message=f"Attendance marked for {len(attendance_records)} person(s)"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_error("Mark Attendance", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to mark attendance: {str(e)}"
        )


@router.get("/attendance/today")
async def get_today_attendance(db: Session = Depends(get_db)):
    """
    Get today's attendance records
    
    Args:
        db: Database session
        
    Returns:
        List of today's attendance records
    """
    try:
        attendance_logs = crud.get_attendance_by_date(db, datetime.now().date())
        
        records = []
        for log in attendance_logs:
            records.append({
                "user_id": log.user_id,
                "name": log.user_name,
                "timestamp": log.timestamp.isoformat(),
                "status": log.status,
                "confidence": float(log.confidence) if log.confidence else None
            })
        
        return {
            "success": True,
            "date": datetime.now().date().isoformat(),
            "records": records,
            "total_present": len(records)
        }
        
    except Exception as e:
        log_error("Get Today Attendance", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch today's attendance: {str(e)}"
        )


@router.get("/attendance/report")
async def get_attendance_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    user_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get attendance report for a date range
    
    Args:
        start_date: Start date for the report
        end_date: End date for the report
        user_id: Optional user ID to filter by
        db: Database session
        
    Returns:
        Attendance report data with statistics
    """
    try:
        # Set defaults
        if end_date is None:
            end_date = datetime.now().date()
        if start_date is None:
            start_date = end_date - timedelta(days=30)
        
        # Get attendance records
        attendance_logs = crud.get_attendance_by_date_range(
            db, start_date, end_date, user_id
        )
        
        records = []
        user_stats = {}
        
        for log in attendance_logs:
            records.append({
                "user_id": log.user_id,
                "name": log.user_name,
                "timestamp": log.timestamp.isoformat(),
                "status": log.status,
                "confidence": float(log.confidence) if log.confidence else None
            })
            
            # Track per-user statistics
            if log.user_id not in user_stats:
                user_stats[log.user_id] = {
                    "name": log.user_name,
                    "present_days": 0,
                    "total_days": 0
                }
            
            user_stats[log.user_id]["total_days"] += 1
            if log.status == "present":
                user_stats[log.user_id]["present_days"] += 1
        
        # Calculate overall statistics
        total_days = (end_date - start_date).days + 1
        present_days = len([r for r in records if r["status"] == "present"])
        absent_days = total_days - present_days if not user_id else 0
        attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0
        
        # Calculate per-user attendance rates
        user_statistics = []
        for uid, stats in user_stats.items():
            rate = (stats["present_days"] / stats["total_days"] * 100) if stats["total_days"] > 0 else 0
            user_statistics.append({
                "user_id": uid,
                "name": stats["name"],
                "present_days": stats["present_days"],
                "total_days": stats["total_days"],
                "attendance_rate": round(rate, 2)
            })
        
        return {
            "success": True,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "records": records,
            "statistics": {
                "total_days": total_days,
                "present_days": present_days,
                "absent_days": absent_days,
                "attendance_rate": round(attendance_rate, 2)
            },
            "user_statistics": user_statistics
        }
        
    except Exception as e:
        log_error("Get Attendance Report", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate attendance report: {str(e)}"
        )


@router.get("/attendance/user/{user_id}")
async def get_user_attendance(
    user_id: str,
    limit: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get attendance history for a specific user
    
    Args:
        user_id: ID of the user
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        User's attendance history with statistics
    """
    try:
        # Verify user exists
        user = crud.get_user(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get attendance history
        attendance_logs = crud.get_user_attendance_history(db, user_id, limit)
        
        records = []
        present_count = 0
        
        for log in attendance_logs:
            records.append({
                "timestamp": log.timestamp.isoformat(),
                "status": log.status,
                "confidence": float(log.confidence) if log.confidence else None
            })
            
            if log.status == "present":
                present_count += 1
        
        total_count = len(records)
        attendance_rate = (present_count / total_count * 100) if total_count > 0 else 0
        
        return {
            "success": True,
            "user_id": user_id,
            "name": user.name,
            "records": records,
            "statistics": {
                "total_records": total_count,
                "present_count": present_count,
                "attendance_rate": round(attendance_rate, 2)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_error("Get User Attendance", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch user attendance: {str(e)}"
        )


@router.get("/attendance/statistics")
async def get_attendance_statistics(db: Session = Depends(get_db)):
    """
    Get overall attendance statistics
    
    Args:
        db: Database session
        
    Returns:
        Attendance statistics and analytics
    """
    try:
        # Get total registered users
        all_users = crud.get_all_users(db)
        total_registered = len(all_users)
        
        # Get today's attendance
        today_logs = crud.get_attendance_by_date(db, datetime.now().date())
        today_present = len(today_logs)
        today_absent = total_registered - today_present
        
        # Get overall attendance statistics
        all_logs = crud.get_all_attendance_logs(db)
        total_logs = len(all_logs)
        present_logs = len([log for log in all_logs if log.status == "present"])
        
        overall_rate = (present_logs / total_logs * 100) if total_logs > 0 else 0
        
        # Get recent activity
        recent_logs = crud.get_recent_attendance_logs(db, limit=10)
        recent_activity = []
        
        for log in recent_logs:
            recent_activity.append({
                "user_id": log.user_id,
                "name": log.user_name,
                "timestamp": log.timestamp.isoformat(),
                "status": log.status
            })
        
        return {
            "success": True,
            "total_registered": total_registered,
            "today_present": today_present,
            "today_absent": today_absent,
            "overall_rate": round(overall_rate, 2),
            "total_attendance_records": total_logs,
            "recent_activity": recent_activity
        }
        
    except Exception as e:
        log_error("Get Attendance Statistics", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch attendance statistics: {str(e)}"
        )
