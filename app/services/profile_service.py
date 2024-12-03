import logging
from datetime import datetime
from app import db
from app.models import User, Direction, Reference, UserProfile
from app.services.chat_service import create_chat_service

logger = logging.getLogger('counsel_windsurf.profile_service')

class ProfileService:
    def __init__(self):
        self.chat_service = create_chat_service("profile")
        logger.info("🧑‍🤝‍🧑 Initialized Profile Service")
    
    def _generate_profile_prompt(self, user):
        """Generate a prompt for the LLM based on user's directions and references."""
        directions = Direction.query.filter_by(author=user).order_by(Direction.timestamp.desc()).all()
        references = Reference.query.filter_by(author=user).order_by(Reference.timestamp.desc()).all()
        
        prompt = f"Create a concise profile summary for a person based on their growth directions and references. Here's their data:\n\n"
        
        if directions:
            prompt += "Growth Directions:\n"
            for direction in directions:
                prompt += f"- {direction.title}: {direction.description}\n"
        
        if references:
            prompt += "\nReferences:\n"
            for reference in references:
                prompt += f"- {reference.title}: {reference.description}\n"
        
        prompt += "\nBased on this information, provide a concise profile summary that captures:"
        prompt += "\n1. Their main areas of growth and interest"
        prompt += "\n2. Key patterns or themes in their journey"
        prompt += "\n3. What seems to motivate or inspire them"
        prompt += "\nMake it personal and encouraging, but keep it under 200 words."
        
        return prompt
    
    def generate_profile(self, user):
        """Generate a new profile for the user based on their directions and references."""
        try:
            logger.info(f"🔄 Generating new profile for user: {user.username}")
            
            # Get existing profile first
            existing_profile = self.get_latest_profile(user)
            if existing_profile:
                # If we have a recent profile and hit rate limit, return existing
                try:
                    # Generate the prompt
                    prompt = self._generate_profile_prompt(user)
                    
                    # Get response from LLM
                    response, is_complete, _, _ = self.chat_service.chat(prompt, [])
                    
                    if not is_complete:
                        logger.error(f"❌ Failed to generate complete profile for user: {user.username}")
                        return existing_profile
                    
                    # Create new profile
                    profile = UserProfile(
                        author=user,
                        description=response,
                        timestamp=datetime.utcnow()
                    )
                    
                    # Save to database
                    db.session.add(profile)
                    db.session.commit()
                    
                    logger.info(f"✅ Successfully generated new profile for user: {user.username}")
                    return profile
                    
                except Exception as e:
                    if "rate limit exceeded" in str(e).lower():
                        logger.warning(f"⚠️ Rate limit hit, using existing profile for user: {user.username}")
                        return existing_profile
                    raise
            else:
                # For new users without a profile, use a simple template
                profile = UserProfile(
                    author=user,
                    description="Start your growth journey by adding directions and references. Your profile will be automatically generated as you share more about your aspirations and inspirations.",
                    timestamp=datetime.utcnow()
                )
                db.session.add(profile)
                db.session.commit()
                return profile
                
        except Exception as e:
            logger.error(f"❌ Error generating profile for user {user.username}: {str(e)}")
            db.session.rollback()
            # Return existing profile if available, otherwise return None
            return existing_profile if existing_profile else None
    
    def get_latest_profile(self, user):
        """Get the user's most recent profile."""
        return UserProfile.query.filter_by(author=user).order_by(UserProfile.timestamp.desc()).first()
    
    def should_update_profile(self, user):
        """Check if user's profile should be updated based on recent changes."""
        latest_profile = self.get_latest_profile(user)
        if not latest_profile:
            return True
            
        # Check if there are any directions or references newer than the latest profile
        latest_direction = Direction.query.filter_by(author=user).order_by(Direction.timestamp.desc()).first()
        latest_reference = Reference.query.filter_by(author=user).order_by(Reference.timestamp.desc()).first()
        
        if latest_direction and latest_direction.timestamp > latest_profile.timestamp:
            return True
        if latest_reference and latest_reference.timestamp > latest_profile.timestamp:
            return True
            
        return False

def create_profile_service():
    """Create and return an instance of ProfileService."""
    return ProfileService()
