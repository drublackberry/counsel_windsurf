import os
import logging

logger = logging.getLogger('counsel_windsurf.utils.api_keys')

def get_groq_api_key() -> str:
    """
    Safely retrieve the GROQ API key from environment variables.
    
    Returns:
        str: The GROQ API key if valid
        
    Raises:
        ValueError: If the API key is not found or invalid
    """
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        logger.error("GROQ_API_KEY not found in environment variables")
        raise ValueError("GROQ_API_KEY must be set in environment variables")
        
    if not api_key.startswith('gsk_'):
        logger.error("GROQ_API_KEY does not start with 'gsk_'. Please check the key format.")
        raise ValueError("GROQ_API_KEY must start with 'gsk_'")
    
    # Log safely (only first 4 chars and length)
    key_prefix = api_key[:4] if len(api_key) >= 4 else api_key
    key_length = len(api_key)
    logger.debug(f"API key starts with '{key_prefix}...' and is {key_length} characters long")
    
    if not api_key.startswith('gsk_'):
        logger.error("GROQ_API_KEY does not start with 'gsk_'. Please check the key format.")
        raise ValueError("GROQ_API_KEY must start with 'gsk_'")
       

    return api_key
