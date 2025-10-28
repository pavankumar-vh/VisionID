"""
Face Detector Service - RetinaFace Implementation
Handles face detection in images using InsightFace's RetinaFace model
"""

import numpy as np
from typing import List, Tuple, Optional, Dict
import insightface
from insightface.app import FaceAnalysis


class FaceDetector:
    """
    Face detection service using InsightFace RetinaFace model
    Provides high-accuracy face detection with bounding boxes and landmarks
    """
    
    def __init__(self, ctx_id: int = 0, det_size: Tuple[int, int] = (640, 640)):
        """
        Initialize face detector
        
        Args:
            ctx_id: GPU context ID (-1 for CPU, 0+ for GPU)
            det_size: Detection size (width, height)
        """
        self.ctx_id = ctx_id
        self.det_size = det_size
        
        # Initialize InsightFace FaceAnalysis with RetinaFace detector
        self.app = FaceAnalysis(providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
        self.app.prepare(ctx_id=ctx_id, det_size=det_size)
        
    def detect_faces(self, image: np.ndarray, threshold: float = 0.5) -> List[Dict]:
        """
        Detect faces in an image
        
        Args:
            image: Input image as numpy array (BGR format)
            threshold: Detection confidence threshold
            
        Returns:
            List of detected faces with bounding boxes, landmarks, and cropped images
        """
        # Detect faces using InsightFace
        faces = self.app.get(image)
        
        detected_faces = []
        for face in faces:
            # Extract face information
            bbox = face.bbox.astype(int)  # [x1, y1, x2, y2]
            confidence = float(face.det_score)
            
            # Filter by confidence threshold
            if confidence < threshold:
                continue
            
            # Crop face from image
            x1, y1, x2, y2 = bbox
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(image.shape[1], x2), min(image.shape[0], y2)
            
            cropped_face = image[y1:y2, x1:x2]
            
            # Get landmarks if available
            landmarks = face.kps.astype(int).tolist() if hasattr(face, 'kps') else None
            
            face_data = {
                'bbox': bbox.tolist(),
                'confidence': confidence,
                'landmarks': landmarks,
                'cropped_face': cropped_face,
                'face_obj': face  # Store original face object for embedding
            }
            
            detected_faces.append(face_data)
        
        return detected_faces
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for detection
        
        Args:
            image: Input image
            
        Returns:
            Preprocessed image
        """
        # Convert to RGB if needed
        if len(image.shape) == 2:  # Grayscale
            image = np.stack([image] * 3, axis=-1)
        elif image.shape[2] == 4:  # RGBA
            image = image[:, :, :3]
        
        return image
    
    def get_face_count(self, image: np.ndarray) -> int:
        """
        Get the number of faces in an image
        
        Args:
            image: Input image
            
        Returns:
            Number of detected faces
        """
        faces = self.detect_faces(image)
        return len(faces)
