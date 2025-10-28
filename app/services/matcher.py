"""
Face Matcher Service - Embedding Comparison & Matching
Compares face embeddings to find matches in the database
"""

import numpy as np
from typing import List, Tuple, Optional


class FaceMatcher:
    """
    Face matching service for comparing embeddings
    Uses cosine similarity for face matching with configurable threshold
    """
    
    def __init__(self, similarity_threshold: float = 0.6):
        """
        Initialize face matcher
        
        Args:
            similarity_threshold: Minimum similarity score for a match (0.0 - 1.0)
        """
        self.similarity_threshold = similarity_threshold
        
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between 0 and 1
        """
        # Cosine similarity
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)
    
    def match_embedding(
        self,
        query_embedding: np.ndarray,
        known_embeddings: List[Tuple[str, np.ndarray]],
        threshold: float = None
    ) -> Optional[Tuple[str, float]]:
        """
        Match a query embedding against known embeddings
        
        Args:
            query_embedding: Embedding to match
            known_embeddings: List of (user_id, embedding) tuples
            threshold: Override default similarity threshold
            
        Returns:
            (user_id, similarity_score) of best match or None if no match above threshold
        """
        if threshold is None:
            threshold = self.similarity_threshold
        
        best_match = None
        best_score = threshold
        
        for user_id, db_embedding in known_embeddings:
            similarity = self.compute_similarity(query_embedding, db_embedding)
            
            if similarity > best_score:
                best_score = similarity
                best_match = (user_id, similarity)
        
        return best_match
    
    def find_match(
        self, 
        query_embedding: np.ndarray, 
        database_embeddings: List[Tuple[str, np.ndarray]]
    ) -> Optional[Tuple[str, float]]:
        """
        Find the best match for a query embedding in the database
        (Alias for match_embedding for backward compatibility)
        
        Args:
            query_embedding: Embedding to match
            database_embeddings: List of (user_id, embedding) tuples
            
        Returns:
            (user_id, similarity_score) of best match or None if no match
        """
        return self.match_embedding(query_embedding, database_embeddings)
    
    def find_all_matches(
        self,
        query_embeddings: List[np.ndarray],
        database_embeddings: List[Tuple[str, np.ndarray]],
        threshold: float = None
    ) -> List[Optional[Tuple[str, float]]]:
        """
        Find matches for multiple query embeddings
        
        Args:
            query_embeddings: List of embeddings to match
            database_embeddings: List of (user_id, embedding) tuples
            threshold: Override default similarity threshold
            
        Returns:
            List of matches (user_id, score) or None for each query
        """
        matches = []
        for query_emb in query_embeddings:
            match = self.match_embedding(query_emb, database_embeddings, threshold)
            matches.append(match)
        return matches
    
    def is_match(self, embedding1: np.ndarray, embedding2: np.ndarray, threshold: float = None) -> bool:
        """
        Check if two embeddings match
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            threshold: Override default similarity threshold
            
        Returns:
            True if embeddings match, False otherwise
        """
        if threshold is None:
            threshold = self.similarity_threshold
            
        similarity = self.compute_similarity(embedding1, embedding2)
        return similarity >= threshold
    
    def get_top_matches(
        self,
        query_embedding: np.ndarray,
        database_embeddings: List[Tuple[str, np.ndarray]],
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Get top K matches for a query embedding
        
        Args:
            query_embedding: Embedding to match
            database_embeddings: List of (user_id, embedding) tuples
            top_k: Number of top matches to return
            
        Returns:
            List of (user_id, similarity_score) tuples, sorted by score (descending)
        """
        similarities = []
        
        for user_id, db_embedding in database_embeddings:
            similarity = self.compute_similarity(query_embedding, db_embedding)
            similarities.append((user_id, similarity))
        
        # Sort by similarity score (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top K
        return similarities[:top_k]
