import os
import httpx
import numpy as np
import json
import logging

logger = logging.getLogger('counsel_windsurf.embedding_service')

class EmbeddingService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            logger.error("GROQ_API_KEY not found in environment variables")
            raise ValueError("GROQ_API_KEY must be set in environment variables")
        logger.info("Initializing Groq API configuration")
        
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "mixtral-8x7b-32768"  # Using Mixtral model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def create_embedding(self, text):
        """Create an embedding for the given text using Groq API."""
        try:
            logger.debug(f"Creating embedding for text: {text[:100]}...")
            
            # Prepare the message for embedding generation
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": text}
            ]
            
            # Make request to Groq API
            response = httpx.post(
                self.base_url,
                headers=self.headers,
                json={
                    "model": self.model,
                    "messages": messages
                }
            )
                
            if response.status_code == 200:
                response_data = response.json()
                    
                # Extract the assistant's response
                assistant_message = response_data['choices'][0]['message']['content']
                    
                # Convert the response to a numpy array (simple approach)
                # Using the hash of the response as a basic numerical representation
                embedding = np.array([hash(word) for word in assistant_message.split()])
                    
                logger.info("Successfully created embedding")
                return embedding, response_data
            else:
                logger.error(f"Error from Groq API: {response.text}")
                return None, None
                    
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            return None, None

    def compute_similarity(self, embedding1, embedding2):
        """Compute cosine similarity between two embeddings."""
        try:
            if embedding1 is None or embedding2 is None:
                return 0.0
                
            # Ensure both embeddings have the same length
            min_length = min(len(embedding1), len(embedding2))
            embedding1 = embedding1[:min_length]
            embedding2 = embedding2[:min_length]
            
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
