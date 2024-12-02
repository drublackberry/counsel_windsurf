import httpx
import logging
from typing import List, Tuple, Optional
import json
from abc import ABC, abstractmethod
from app.utils import get_groq_api_key

logger = logging.getLogger('counsel_windsurf.chat_service')

class BaseChatService(ABC):
    """Base class for all chat services."""
    
    def __init__(self):
        self.api_key = get_groq_api_key()
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "mixtral-8x7b-32768"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Return the system prompt for this chat service."""
        pass
    
    @property
    @abstractmethod
    def completion_token(self) -> str:
        """Return the completion token that marks the end of the conversation."""
        pass

    def generate_short_summary(self, full_text: str) -> str:
        """Generate a short (less than 5 words) summary."""
        try:
            messages = [
                {"role": "system", "content": "You are a concise summarizer. Create a clear, impactful summary using 5 or fewer words."},
                {"role": "user", "content": f"Please summarize this in 5 or fewer words: {full_text}"}
            ]
            
            request_payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 50
            }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    self.base_url,
                    headers=self.headers,
                    json=request_payload
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    short_summary = response_data['choices'][0]['message']['content'].strip()
                    logger.info(f"Generated short summary: {short_summary}")
                    return short_summary
                else:
                    logger.error(f"Failed to generate short summary: {response.text}")
                    return "Summary"  # Fallback
                    
        except Exception as e:
            logger.error(f"Error generating short summary: {str(e)}")
            return "Summary"  # Fallback

    def chat(self, user_input: str, conversation_history: List[dict] = None) -> Tuple[str, bool, str, str]:
        """Process user input and return AI response with summary if complete."""
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
            
            request_payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1024
            }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    self.base_url,
                    headers=self.headers,
                    json=request_payload
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    assistant_message = response_data['choices'][0]['message']['content']
                    
                    # Format the full conversation including the latest exchange
                    updated_messages = conversation_history + [
                        {"role": "user", "content": user_input},
                        {"role": "assistant", "content": assistant_message}
                    ]
                    full_conversation = "\n\n".join([
                        f"{'You' if msg['role'] == 'user' else 'AI Counselor'}: {msg['content']}"
                        for msg in updated_messages
                    ])
                    
                    # Check if conversation is complete
                    is_complete = self.completion_token in assistant_message
                    if is_complete:
                        processed_message = assistant_message.split(self.completion_token)[1].strip()
                        short_summary = self.generate_short_summary(processed_message)
                    else:
                        processed_message = assistant_message
                        short_summary = None
                    
                    return processed_message, is_complete, full_conversation, short_summary
                    
                else:
                    error_body = response.text
                    logger.error(f"Error response from Groq API (Status {response.status_code}): {error_body}")
                    return f"I apologize, but I encountered an error (Status {response.status_code}). Please try again.", False, "", ""
                    
        except Exception as e:
            logger.error(f"Unexpected error in chat: {str(e)}", exc_info=True)
            return f"I apologize, but I encountered an unexpected error: {str(e)}. Please try again.", False, "", ""


class GrowthDirectionChatService(BaseChatService):
    """Chat service specifically for exploring growth directions."""
    
    @property
    def system_prompt(self) -> str:
        return """You are a growth counselor helping users identify and articulate their growth directions. 
        Your goal is to have a conversation that helps users clarify their growth aspirations.
        Ask relevant follow-up questions to understand their goals better.
        When you feel you have a clear understanding, respond with a message starting with the specific token '[DIRCOMP]' 
        followed by a concise summary of their growth direction."""
    
    @property
    def completion_token(self) -> str:
        return "[DIRCOMP]"


class IdolsChatService(BaseChatService):
    """Chat service for exploring personal idols and role models."""
    
    @property
    def system_prompt(self) -> str:
        return """You are a counselor helping users identify and articulate their personal idols and role models.
        Your goal is to have a conversation that helps users reflect on who they admire and why.
        Ask relevant follow-up questions to understand their perspective better, try to ask only one question at a time and do at least two  iterations.
        Only when you feel you have a clear understanding of why the user admires this idol, respond with a message starting with the specific token '[IDOLCOMP]'
        followed by a concise summary of their idols and what they admire about them."""
    
    @property
    def completion_token(self) -> str:
        return "[IDOLCOMP]"


# Factory function to create chat services
def create_chat_service(chat_type: str) -> BaseChatService:
    """Create a chat service instance based on the specified type."""
    services = {
        "growth": GrowthDirectionChatService,
        "idols": IdolsChatService,
    }
    
    service_class = services.get(chat_type)
    if not service_class:
        raise ValueError(f"Unknown chat type: {chat_type}")
    
    return service_class()
