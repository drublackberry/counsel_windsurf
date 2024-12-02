import logging

logger = logging.getLogger('counsel_windsurf.text_processing')

def is_direction_complete(text: str, completion_token: str) -> tuple[bool, str]:
    """
    Check if a direction is complete and extract the processed message.
    
    Args:
        text (str): The text to check
        completion_token (str): The token that marks completion
        
    Returns:
        tuple[bool, str]: A tuple containing:
            - bool: True if the direction is complete, False otherwise
            - str: The processed message (everything after the completion token if complete,
                  or the original message if not complete)
    """
    if completion_token in text:
        return True, text.split(completion_token)[1].strip()
    return False, text
