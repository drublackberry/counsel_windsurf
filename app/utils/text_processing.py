import logging

logger = logging.getLogger('counsel_windsurf.text_processing')

def is_direction_complete(text: str, completion_token='[DIRCOMP]') -> tuple[bool, str]:
    """Check if the direction is complete and extract the summary.
    
    Args:
        text (str): The text to check for completion token and extract summary from
        
    Returns:
        tuple[bool, str]: A tuple containing:
            - bool: True if the direction is complete, False otherwise
            - str: The cleaned summary text if complete, original text if not
    """
  
    try:
        if completion_token in text:
            # Split on token and take everything after it
            summary = text.split(completion_token)[1].strip()
            logger.info(f"Direction complete, extracted summary: {summary[:100]}...")
            return True, summary
            
        return False, text
        
    except Exception as e:
        logger.error(f"Error processing direction text: {str(e)}")
        return False, text
