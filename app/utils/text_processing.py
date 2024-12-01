import re
import logging

logger = logging.getLogger('counsel_windsurf.utils.text_processing')

def is_direction_complete(message: str) -> tuple[bool, str]:
    """
    Check if a message indicates direction completion, handling various formats.
    
    Args:
        message: The message to check
        
    Returns:
        tuple[bool, str]: (is_complete, cleaned_message)
            - is_complete: True if the message indicates completion
            - cleaned_message: The cleaned message with standardized format
    """
    # Look for [DIRECTIONCOMPLETE] token
    if '[DIRECTIONCOMPLETE]' in message.upper():
        # Extract everything after the completion marker
        full_text = message.strip()
        marker_pos = full_text.upper().find('[DIRECTIONCOMPLETE]')
        summary = full_text[marker_pos + 18:].strip()  # 18 is length of [DIRECTIONCOMPLETE]
        logger.debug(f"Found direction completion, summary: {summary}")
        return True, summary
    
    logger.debug("No direction completion found")
    return False, message
