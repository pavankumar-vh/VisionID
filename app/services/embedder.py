"""
Face Embedder Service - ArcFace Implementation
Generates face embeddings for recognition using InsightFace's ArcFace model
"""

import numpy as np
from typing import Optional, List


class FaceEmbedder:
    """
    Face embedding service using InsightFace ArcFace model
    Converts detected faces into 512-dimensional embeddings
    """
    
    def __init__(self, ctx_id: int = 0):
        """
        Initialize face embedder
        
        Args:
            ctx_id: GPU context ID (-1 for CPU, 0+ for GPU)
        """
        self.ctx_id = ctx_id
        self.embedding_size = 512
        # Note: Embeddings are extracted from face objects provided by FaceAnalysis
        # No separate model initialization needed as it's part of FaceAnalysis
        
    def get_embedding(self, face_obj) -> Optional[np.ndarray]:
        """
        Generate embedding for a face object from InsightFace
        
        Args:
            face_obj: Face object from InsightFace FaceAnalysis
            
        Returns:
            512-dimensional embedding vector or None if failed
        """
        try:
            # Extract embedding from face object
            if hasattr(face_obj, 'embedding'):
                embedding = face_obj.embedding
                # Normalize the embedding
                return self.normalize_embedding(embedding)
            elif hasattr(face_obj, 'normed_embedding'):
                # Already normalized
                return face_obj.normed_embedding
            else:
                return None
        except Exception as e:
            print(f"Error extracting embedding: {e}")
            return None
    
    def get_embeddings_batch(self, face_objects: list) -> List[np.ndarray]:
        """
        Generate embeddings for multiple faces
        
        Args:
            face_objects: List of face objects from InsightFace
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        for face_obj in face_objects:
            emb = self.get_embedding(face_obj)
            if emb is not None:
                embeddings.append(emb)
        return embeddings
    
    def normalize_embedding(self, embedding: np.ndarray) -> np.ndarray:
        """
        Normalize embedding vector to unit length
        
        Args:
            embedding: Raw embedding vector
            
        Returns:
            Normalized embedding vector
        """
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return embedding
        return embedding / norm
    
    def embedding_to_bytes(self, embedding: np.ndarray) -> bytes:
        """
        Convert embedding to bytes for database storage
        
        Args:
            embedding: Numpy embedding array
            
        Returns:
            Embedding as bytes
        """
        return embedding.tobytes()
    
    def bytes_to_embedding(self, embedding_bytes: bytes) -> np.ndarray:
        """
        Convert bytes back to embedding array
        
        Args:
            embedding_bytes: Embedding stored as bytes
            
        Returns:
            Numpy embedding array
        """
        return np.frombuffer(embedding_bytes, dtype=np.float32)
