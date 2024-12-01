import httpx
import logging
from typing import List, Tuple
import json
from app.utils import get_groq_api_key, is_direction_complete

logger = logging.getLogger('counsel_windsurf.chat_service')
COMPLETION_TOKEN = '[DIRCOMP]'

class ChatService:
    def __init__(self):
        self.api_key = get_groq_api_key()
     
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "mixtral-8x7b-32768"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.system_prompt = f"""You are a growth counselor helping users identify and articulate their growth directions. 
        Your goal is to have a conversation that helps users clarify their growth aspirations.
        Ask relevant follow-up questions to understand their goals better.
        When you feel you have a clear understanding, respond with a message starting with the specific token '{COMPLETION_TOKEN}' 
        followed by a concise summary of their growth direction."""
        
    def chat(self, user_input: str, conversation_history: List[dict] = None) -> Tuple[str, bool, str]:
        """Process user input and return AI response."""
        if conversation_history is None:
            conversation_history = []
            
        try:
            # Prepare messages for the API
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": user_input})
            
            # Log the full conversation context
            logger.info("=== Conversation Context ===")
            for msg in messages:
                logger.info(f"{msg['role'].upper()}: {msg['content']}")
            logger.info("=========================")
            
            # Log the request payload for debugging
            request_payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1024
            }
            logger.debug(f"Request payload: {json.dumps(request_payload, indent=2)}")
            
            # Make request to Groq API
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    self.base_url,
                    headers=self.headers,
                    json=request_payload
                )
                
                # Log the response status and headers
                logger.debug(f"Response status: {response.status_code}")
                
                if response.status_code == 200:
                    response_data = response.json()
                    assistant_message = response_data['choices'][0]['message']['content']
                    
                    # Log the full response
                    logger.info("=== AI Response ===")
                    logger.info(f"Raw response: {assistant_message}")
                    logger.info("=================")
                    
                    # Use text processing utility to check completion and get summary
                    is_complete, processed_message = is_direction_complete(assistant_message, COMPLETION_TOKEN)
                    
                    # Log completion status and processed message
                    logger.info(f"Direction complete: {is_complete}")
                    if is_complete:
                        logger.info(f"Processed summary: {processed_message}")
                    
                    return processed_message, is_complete, assistant_message
                    
                else:
                    error_body = response.text
                    logger.error(f"Error response from Groq API (Status {response.status_code}): {error_body}")
                    return f"I apologize, but I encountered an error (Status {response.status_code}). Please try again.", False, ""
                    
        except httpx.TimeoutException as e:
            logger.error(f"Timeout error when calling Groq API: {str(e)}")
            return "I apologize, but the request timed out. Please try again.", False, ""
        except httpx.RequestError as e:
            logger.error(f"Network error when calling Groq API: {str(e)}")
            return "I apologize, but there was a network error. Please try again.", False, ""
        except KeyError as e:
            logger.error(f"Unexpected response format from Groq API: {str(e)}")
            return "I apologize, but I received an unexpected response format. Please try again.", False, ""
        except Exception as e:
            logger.error(f"Unexpected error in chat: {str(e)}", exc_info=True)
            return f"I apologize, but I encountered an unexpected error: {str(e)}. Please try again.", False, ""
