"""
Registration Routes - User & Face Registration Endpoints
"""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
import time

from app.services.detector import FaceDetector
from app.services.embedder import FaceEmbedder
from app.models.database import get_db
from app.models import crud
from app.utils.image_utils import read_image_file, validate_image, save_image
from app.utils.logger import log_registration, log_error

router = APIRouter()

# Initialize services (cached)
face_detector = None
face_embedder = None


def get_services():
    """Get or initialize face detection and embedding services"""
    global face_detector, face_embedder
    if face_detector is None:
        face_detector = FaceDetector(ctx_id=0)  # 0 for GPU, -1 for CPU
    if face_embedder is None:
        face_embedder = FaceEmbedder(ctx_id=0)
    return face_detector, face_embedder


class RegistrationResponse(BaseModel):
    """Response model for user registration"""
    success: bool
    user_id: Optional[str] = None
    name: str
    message: str
    embedding_size: Optional[int] = None


@router.post("/register", response_model=RegistrationResponse)
async def register_user(
    name: str = Form(...),
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Register a new user with their face
    
    Args:
        name: Name of the person to register
        file: Image file containing the person's face
        metadata: Optional additional metadata (JSON string)
        db: Database session
        
    Returns:
        RegistrationResponse with registration status
    """
    try:
        # Check if user already exists
        existing_user = crud.get_user_by_name(db, name)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail=f"User with name '{name}' already exists"
            )
        
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
        detector, embedder = get_services()
        
        # Detect faces
        detected_faces = detector.detect_faces(image, threshold=0.5)
        
        if len(detected_faces) == 0:
            raise HTTPException(
                status_code=400,
                detail="No face detected in the image. Please upload a clear face photo."
            )
        
        if len(detected_faces) > 1:
            raise HTTPException(
                status_code=400,
                detail=f"Multiple faces detected ({len(detected_faces)}). Please upload an image with only one face."
            )
        
        # Get the single face
        face_data = detected_faces[0]
        face_obj = face_data['face_obj']
        
        # Extract embedding
        embedding = embedder.get_embedding(face_obj)
        
        if embedding is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to extract face embedding"
            )
        
        # Save image to uploads folder
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        timestamp = int(time.time())
        image_filename = f"{name.replace(' ', '_')}_{timestamp}.jpg"
        image_path = os.path.join(upload_dir, image_filename)
        
        save_image(image, image_path)
        
        # Convert embedding to bytes for storage
        embedding_bytes = embedder.embedding_to_bytes(embedding)
        
        # Create user in database
        user = crud.create_user(
            db=db,
            name=name,
            embedding=embedding_bytes,
            image_path=image_path,
            metadata=metadata
        )
        
        # Log registration
        log_registration(user.id, name, True)
        
        return RegistrationResponse(
            success=True,
            user_id=user.id,
            name=user.name,
            embedding_size=len(embedding),
            message=f"User '{name}' registered successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_error("Registration", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(e)}"
        )


@router.get("/register/users")
async def list_registered_users(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get list of all registered users
    
    Args:
        limit: Maximum number of users to return
        offset: Number of users to skip
        db: Database session
        
    Returns:
        List of registered users
    """
    try:
        users = crud.get_all_users(db, skip=offset, limit=limit)
        total_users = len(crud.get_all_users(db, skip=0, limit=10000))
        
        user_list = []
        for user in users:
            user_list.append({
                "user_id": user.id,
                "name": user.name,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "image_path": user.image_path
            })
        
        return {
            "success": True,
            "users": user_list,
            "total": total_users,
            "limit": limit,
            "offset": offset,
            "message": f"Retrieved {len(user_list)} users"
        }
        
    except Exception as e:
        log_error("List Users", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve users: {str(e)}"
        )


@router.delete("/register/user/{user_id}")
async def delete_user(user_id: str, db: Session = Depends(get_db)):
    """
    Delete a registered user
    
    Args:
        user_id: ID of the user to delete
        db: Database session
        
    Returns:
        Deletion status
    """
    try:
        success = crud.delete_user(db, user_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID '{user_id}' not found"
            )
        
        return {
            "success": True,
            "user_id": user_id,
            "message": f"User deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_error("Delete User", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete user: {str(e)}"
        )


@router.put("/register/user/{user_id}")
async def update_user(
    user_id: str,
    name: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Update a registered user's information
    
    Args:
        user_id: ID of the user to update
        name: New name for the user
        file: New face image for the user
        db: Database session
        
    Returns:
        Update status
    """
    try:
        # Check if user exists
        user = crud.get_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID '{user_id}' not found"
            )
        
        embedding_bytes = None
        
        # If new image provided, extract new embedding
        if file:
            image_bytes = await file.read()
            is_valid, error_msg = validate_image(image_bytes)
            
            if not is_valid:
                raise HTTPException(status_code=400, detail=error_msg)
            
            image = read_image_file(image_bytes)
            if image is None:
                raise HTTPException(status_code=400, detail="Failed to read image")
            
            # Get services and detect face
            detector, embedder = get_services()
            detected_faces = detector.detect_faces(image, threshold=0.5)
            
            if len(detected_faces) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="No face detected in the new image"
                )
            
            if len(detected_faces) > 1:
                raise HTTPException(
                    status_code=400,
                    detail="Multiple faces detected. Please upload an image with only one face."
                )
            
            face_obj = detected_faces[0]['face_obj']
            embedding = embedder.get_embedding(face_obj)
            
            if embedding is None:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to extract face embedding from new image"
                )
            
            embedding_bytes = embedder.embedding_to_bytes(embedding)
        
        # Update user
        updated_user = crud.update_user(db, user_id, name=name, embedding=embedding_bytes)
        
        if not updated_user:
            raise HTTPException(
                status_code=500,
                detail="Failed to update user"
            )
        
        return {
            "success": True,
            "user_id": user_id,
            "name": updated_user.name,
            "message": "User updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_error("Update User", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update user: {str(e)}"
        )
