import os
import httpx
import numpy as np
import json
import logging

__all__ = ['EmbeddingService', 'create_embedding_service']

logger = logging.getLogger('counsel_windsurf.embedding_service')

class EmbeddingService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('HUGGINGFACE_API_KEY')
        if not self.api_key:
            logger.error("HUGGINGFACE_API_KEY not found in environment variables")
            raise ValueError("HUGGINGFACE_API_KEY must be set in environment variables")
        logger.info("Initializing HuggingFace API configuration")
        
        self.api_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def create_embedding(self, text):
        """Create an embedding for the given text using HuggingFace's sentence-transformers API."""
        try:
            logger.debug(f"Creating embedding for text: {text[:100]}...")
            
            # Make request to HuggingFace API
            response = httpx.post(
                self.api_url,
                headers=self.headers,
                json={"inputs": text, "options": {"wait_for_model": True}}
            )
                
            if response.status_code == 200:
                # HuggingFace returns the embedding directly as a list of floats
                embedding = np.array(response.json())
                logger.info("Successfully created embedding")
                return embedding
            else:
                logger.error(f"Error from HuggingFace API: {response.text}")
                return None
                    
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            return None

    def compute_similarity(self, embedding1, embedding2):
        """Compute cosine similarity between two embeddings."""
        try:
            if embedding1 is None or embedding2 is None:
                return 0.0
            
            # Compute cosine similarity
            dot_product = np.dot(embedding1, embedding2)
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error computing similarity: {str(e)}")
            return 0.0

    def health_check(self):
        """Check if the HuggingFace API is accessible and responding."""
        try:
            # Try to create a simple embedding as a health check
            test_embedding = self.create_embedding("health check")
            if test_embedding is not None:
                logger.info("")
                return True, "HuggingFace API is healthy"
            else:
                logger.error("")
                return False, "HuggingFace API failed to generate embedding"
        except Exception as e:
            logger.error(f" HuggingFace API health check failed with error: {str(e)}")
            return False, f"HuggingFace API error: {str(e)}"

def create_embedding_service():
    """Create and return an instance of EmbeddingService."""
    return EmbeddingService()
