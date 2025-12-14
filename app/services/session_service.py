"""
Session Management Service
Handles conversation sessions using in-memory storage (can be extended to Redis)
"""
import uuid
import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from collections import OrderedDict

from app.config import settings
from app.models.conversation import Session, Message, ConversationContext

logger = logging.getLogger(__name__)


class SessionService:
    """Service for managing conversation sessions"""
    
    def __init__(self):
        # In-memory session storage (use Redis in production)
        self.sessions: Dict[str, Session] = OrderedDict()
        self.max_sessions = 1000  # Max sessions to keep in memory
        logger.info("Session service initialized (in-memory mode)")
    
    async def create_session(
        self,
        language: str = "hi",
        user_id: Optional[str] = None,
        user_context: Optional[Dict] = None
    ) -> Session:
        """
        Create a new conversation session
        
        Args:
            language: Preferred language for session
            user_id: Optional user identifier
            user_context: Initial context information
            
        Returns:
            New Session object
        """
        try:
            # Generate unique session ID
            session_id = f"sess_{uuid.uuid4().hex[:16]}"
            
            # Calculate expiration
            expires_at = datetime.utcnow() + timedelta(minutes=settings.SESSION_EXPIRE_MINUTES)
            
            # Create context
            context = ConversationContext()
            if user_context:
                context.collected_information = user_context
            
            # Create session
            session = Session(
                session_id=session_id,
                user_id=user_id,
                language=language,
                context=context,
                expires_at=expires_at,
                is_active=True
            )
            
            # Store session
            self.sessions[session_id] = session
            
            # Cleanup if too many sessions
            if len(self.sessions) > self.max_sessions:
                await self._cleanup_oldest_sessions()
            
            logger.info(f"Created session: {session_id} (language: {language})")
            return session
            
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            raise Exception(f"Failed to create session: {str(e)}")
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get session by ID
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session object or None if not found/expired
        """
        try:
            session = self.sessions.get(session_id)
            
            if not session:
                return None
            
            # Check if expired
            if datetime.utcnow() > session.expires_at:
                await self.delete_session(session_id)
                return None
            
            # Check if active
            if not session.is_active:
                return None
            
            return session
            
        except Exception as e:
            logger.error(f"Error getting session {session_id}: {str(e)}")
            return None
    
    async def update_session(
        self,
        session_id: str,
        message: Optional[Message] = None,
        context_updates: Optional[Dict] = None
    ) -> Optional[Session]:
        """
        Update session with new message or context
        
        Args:
            session_id: Session identifier
            message: New message to add
            context_updates: Updates to context
            
        Returns:
            Updated Session object or None
        """
        try:
            session = await self.get_session(session_id)
            if not session:
                return None
            
            # Add message
            if message:
                session.messages.append(message)
            
            # Update context
            if context_updates:
                for key, value in context_updates.items():
                    if key == "current_intent":
                        session.context.current_intent = value
                    elif key == "collected_information":
                        session.context.collected_information.update(value)
                    elif key == "mentioned_schemes":
                        if isinstance(value, list):
                            session.context.mentioned_schemes.extend(value)
                    elif key == "pending_questions":
                        if isinstance(value, list):
                            session.context.pending_questions.extend(value)
                    elif key == "last_topic":
                        session.context.last_topic = value
                    elif key == "clarification_needed":
                        session.context.clarification_needed = value
            
            # Update timestamp
            session.updated_at = datetime.utcnow()
            
            # Extend expiration
            session.expires_at = datetime.utcnow() + timedelta(minutes=settings.SESSION_EXPIRE_MINUTES)
            
            # Store updated session
            self.sessions[session_id] = session
            
            logger.debug(f"Updated session: {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Error updating session {session_id}: {str(e)}")
            return None
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            if session_id in self.sessions:
                del self.sessions[session_id]
                logger.info(f"Deleted session: {session_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {str(e)}")
            return False
    
    async def end_session(self, session_id: str) -> bool:
        """
        Mark session as inactive (soft delete)
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if ended, False otherwise
        """
        try:
            session = self.sessions.get(session_id)
            if session:
                session.is_active = False
                session.updated_at = datetime.utcnow()
                logger.info(f"Ended session: {session_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error ending session {session_id}: {str(e)}")
            return False
    
    async def get_conversation_history(
        self,
        session_id: str,
        limit: int = 10
    ) -> list[Message]:
        """
        Get conversation history for a session
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages to return
            
        Returns:
            List of messages
        """
        try:
            session = await self.get_session(session_id)
            if not session:
                return []
            
            # Return last N messages
            return session.messages[-limit:]
            
        except Exception as e:
            logger.error(f"Error getting conversation history for {session_id}: {str(e)}")
            return []
    
    async def _cleanup_oldest_sessions(self):
        """Remove oldest sessions when limit exceeded"""
        try:
            # Remove 10% of oldest sessions
            num_to_remove = max(1, len(self.sessions) // 10)
            
            # Get oldest session IDs
            oldest_ids = list(self.sessions.keys())[:num_to_remove]
            
            for session_id in oldest_ids:
                del self.sessions[session_id]
            
            logger.info(f"Cleaned up {num_to_remove} oldest sessions")
            
        except Exception as e:
            logger.error(f"Error cleaning up sessions: {str(e)}")
    
    async def cleanup_expired_sessions(self):
        """Remove all expired sessions"""
        try:
            now = datetime.utcnow()
            expired_ids = [
                sid for sid, session in self.sessions.items()
                if now > session.expires_at or not session.is_active
            ]
            
            for session_id in expired_ids:
                del self.sessions[session_id]
            
            if expired_ids:
                logger.info(f"Cleaned up {len(expired_ids)} expired sessions")
            
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {str(e)}")
    
    def get_stats(self) -> Dict:
        """Get session statistics"""
        total = len(self.sessions)
        active = sum(1 for s in self.sessions.values() if s.is_active)
        
        return {
            "total_sessions": total,
            "active_sessions": active,
            "inactive_sessions": total - active
        }


# Singleton instance
session_service = SessionService()


# Background task to cleanup expired sessions
async def cleanup_sessions_task():
    """Background task to periodically cleanup expired sessions"""
    while True:
        await asyncio.sleep(300)  # Run every 5 minutes
        await session_service.cleanup_expired_sessions()
