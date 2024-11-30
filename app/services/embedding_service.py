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
        logger.debug(f"Groq API configuration initialized successfully with model: {self.model}")

    def create_embedding(self, text):
        """Create embedding for the given text using Groq's API"""
        try:
            logger.debug(f"Creating embedding for text: {text[:100]}...")
            
            # Construct a prompt that asks for a structured semantic analysis
            prompt = (
                "Analyze the following text and provide a structured semantic representation. "
                "Include key concepts, relationships, and important context. "
                "Format your response as a list of key points and their relationships."
            )
            
            payload = {
                "messages": [{
                    "role": "system",
                    "content": "You are a semantic analysis assistant that helps create structured representations of text."
                }, {
                    "role": "user",
                    "content": f"{prompt}\n\nText to analyze: {text}"
                }],
                "model": self.model,
                "temperature": 0.0,
                "max_tokens": 1000,
                "top_p": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0
            }
            
            with httpx.Client(timeout=60.0) as client:
                logger.debug(f"Sending request to Groq API with model: {self.model}")
                response = client.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
            
            # Extract the content from the response
            embedding_text = data['choices'][0]['message']['content']
            logger.debug(f"Received response: {embedding_text[:100]}...")
            
            # Convert the text to a numerical embedding using a more sophisticated approach
            # Split into sentences and words for better semantic representation
            sentences = embedding_text.lower().split('.')
            embedding = np.zeros(768)  # Using a 768-dimensional embedding space
            
            for sentence in sentences:
                words = sentence.strip().split()
                for i, word in enumerate(words):
                    # Use position-aware hashing to capture word order
                    hash_val = hash(f"{word}_{i}")
                    embedding[hash_val % 768] += 1.0 / (i + 1)  # Weight by position
            
            # Normalize the embedding
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            
            logger.info("Embedding created successfully")
            return embedding, embedding_text
            
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            return None, None

    def compute_similarity(self, embedding1, embedding2):
        """Compute cosine similarity between two embeddings"""
        if embedding1 is None or embedding2 is None:
            logger.warning("One or both embeddings are None")
            return 0.0
        try:
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            if norm1 == 0 or norm2 == 0:
                logger.warning("One or both embedding norms are zero")
                return 0.0
            similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
            logger.debug(f"Computed similarity: {similarity}")
            return similarity
        except Exception as e:
            logger.error(f"Error computing similarity: {str(e)}")
            return 0.0
