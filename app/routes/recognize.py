"""
Recognition Routes - Face Detection & Recognition Endpoints
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from typing import List
from pydantic import BaseModel
import numpy as np
from sqlalchemy.orm import Session
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.services.detector import FaceDetector
from app.services.embedder import FaceEmbedder
from app.services.matcher import FaceMatcher
from app.models.database import get_db
from app.models import crud
from app.utils.image_utils import read_image_file, validate_image
from app.utils.logger import log_recognition, log_error

router = APIRouter()

# Initialize services (cached in memory)
face_detector = None
face_embedder = None
face_matcher = None
executor = ThreadPoolExecutor(max_workers=4)


def get_face_detector():
    """Get or initialize face detector"""
    global face_detector
    if face_detector is None:
        face_detector = FaceDetector(ctx_id=0)  # 0 for GPU, -1 for CPU
    return face_detector


def get_face_embedder():
    """Get or initialize face embedder"""
    global face_embedder
    if face_embedder is None:
        face_embedder = FaceEmbedder(ctx_id=0)
    return face_embedder


def get_face_matcher():
    """Get or initialize face matcher"""
    global face_matcher
    if face_matcher is None:
        face_matcher = FaceMatcher(similarity_threshold=0.6)
    return face_matcher


class FaceRecognition(BaseModel):
    """Model for individual face recognition result"""
    user_id: str = None
    name: str = "Unknown"
    confidence: float
    similarity: float = 0.0
    bbox: List[int]


class RecognitionResponse(BaseModel):
    """Response model for face recognition"""
    success: bool
    detected_faces: int
    recognitions: List[FaceRecognition]
    message: str


@router.post("/recognize", response_model=RecognitionResponse)
async def recognize_faces(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Recognize faces in an uploaded image
    
    Args:
        file: Image file containing faces to recognize
        db: Database session
        
    Returns:
        RecognitionResponse with detected faces and their identities
    """
    try:
        # Read and validate image
        image_bytes = await file.read()
        is_valid, error_msg = validate_image(image_bytes)
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Convert to numpy array
        image = read_image_file(image_bytes)
        if image is None:
            raise HTTPException(status_code=400, detail="Failed to read image")
        
        # Get services
        detector = get_face_detector()
        embedder = get_face_embedder()
        matcher = get_face_matcher()
        
        # Detect faces
        detected_faces = detector.detect_faces(image, threshold=0.5)
        
        if len(detected_faces) == 0:
            return RecognitionResponse(
                success=True,
                detected_faces=0,
                recognitions=[],
                message="No faces detected in the image"
            )
        
        # Get all known embeddings from database
        db_embeddings_data = crud.get_all_embeddings(db)
        known_embeddings = []
        
        for user_id, emb_bytes in db_embeddings_data:
            emb_array = embedder.bytes_to_embedding(emb_bytes)
            known_embeddings.append((user_id, emb_array))
        
        # Process each detected face concurrently
        async def process_face(face_data):
            """Process a single face asynchronously"""
            face_obj = face_data['face_obj']
            bbox = face_data['bbox']
            det_confidence = face_data['confidence']
            
            # Get embedding for this face (run in thread pool)
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                executor,
                embedder.get_embedding,
                face_obj
            )
            
            if embedding is None:
                return FaceRecognition(
                    user_id=None,
                    name="Unknown",
                    confidence=det_confidence,
                    similarity=0.0,
                    bbox=bbox
                )
            
            # Match against known embeddings
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
                    
                    # Get user details
                    user = crud.get_user(db, user_id)
                    
                    if user:
                        # Log recognition
                        log_recognition(user_id, similarity, True)
                        
                        return FaceRecognition(
                            user_id=user_id,
                            name=user.name,
                            confidence=det_confidence,
                            similarity=similarity,
                            bbox=bbox
                        )
            
            # No match found or no known embeddings
            return FaceRecognition(
                user_id=None,
                name="Unknown",
                confidence=det_confidence,
                similarity=0.0,
                bbox=bbox
            )
        
        # Process all faces concurrently using asyncio.gather
        recognitions = await asyncio.gather(*[process_face(face) for face in detected_faces])
        
        # Create recognition history records
        for recog in recognitions:
            crud.create_recognition_record(
                db=db,
                user_id=recog.user_id,
                user_name=recog.name,
                confidence=str(recog.similarity),
                recognized="true" if recog.user_id else "false"
            )
        
        return RecognitionResponse(
            success=True,
            detected_faces=len(detected_faces),
            recognitions=recognitions,
            message=f"Successfully detected and processed {len(detected_faces)} face(s)"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_error("Recognition", str(e))
        raise HTTPException(status_code=500, detail=f"Recognition failed: {str(e)}")


@router.post("/recognize/video")
async def recognize_video_frame(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Recognize faces in a video frame
    
    Args:
        file: Video frame image to process
        db: Database session
        
    Returns:
        Recognition results for the frame
    """
    # Reuse the same logic as recognize_faces
    return await recognize_faces(file, db)


@router.get("/recognize/history")
async def get_recognition_history(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get recent recognition history
    
    Args:
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of recent recognitions
    """
    try:
        history = crud.get_recognition_history(db, limit=limit)
        
        records = []
        for record in history:
            records.append({
                "id": record.id,
                "user_id": record.user_id,
                "user_name": record.user_name,
                "timestamp": record.timestamp.isoformat() if record.timestamp else None,
                "confidence": record.confidence,
                "recognized": record.recognized == "true"
            })
        
        return {
            "success": True,
            "count": len(records),
            "history": records,
            "message": f"Retrieved {len(records)} recognition records"
        }
        
    except Exception as e:
        log_error("Recognition History", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")
