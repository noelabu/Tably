"""
Conversation memory service for maintaining chat context across requests.
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import threading
from dataclasses import dataclass, asdict
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class ChatMessage:
    """Represents a single message in a conversation."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata or {}
        }

@dataclass
class ConversationSession:
    """Represents a conversation session."""
    session_id: str
    business_id: Optional[str]
    user_id: Optional[str]
    messages: List[ChatMessage]
    created_at: datetime
    last_activity: datetime
    context: Dict[str, Any]

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a message to the conversation."""
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.utcnow(),
            metadata=metadata
        )
        self.messages.append(message)
        self.last_activity = datetime.utcnow()

    def get_recent_messages(self, limit: int = 10) -> List[ChatMessage]:
        """Get the most recent messages."""
        return self.messages[-limit:] if self.messages else []

    def get_conversation_context(self, limit: int = 10) -> str:
        """Get formatted conversation context for the agent."""
        recent_messages = self.get_recent_messages(limit)
        if not recent_messages:
            return ""
        
        context_lines = ["CONVERSATION HISTORY:"]
        for msg in recent_messages:
            timestamp = msg.timestamp.strftime("%H:%M")
            context_lines.append(f"[{timestamp}] {msg.role.title()}: {msg.content}")
        
        context_lines.append("\nPlease continue this conversation naturally, maintaining context from previous messages.")
        return "\n".join(context_lines)

    def extract_order_context(self) -> Dict[str, Any]:
        """Extract order-related context from the conversation."""
        order_context = {
            "mentioned_items": [],
            "dietary_restrictions": [],
            "preferences": [],
            "quantity_requests": [],
            "special_instructions": []
        }
        
        # Simple keyword extraction (could be enhanced with NLP)
        for message in self.messages:
            if message.role == "user":
                content_lower = message.content.lower()
                
                # Look for dietary mentions
                dietary_keywords = ["vegetarian", "vegan", "gluten-free", "keto", "allergic", "allergy"]
                for keyword in dietary_keywords:
                    if keyword in content_lower:
                        order_context["dietary_restrictions"].append(keyword)
                
                # Look for quantity mentions
                quantity_keywords = ["2", "two", "3", "three", "large", "small", "extra"]
                for keyword in quantity_keywords:
                    if keyword in content_lower:
                        order_context["quantity_requests"].append(keyword)
                
                # Look for preference mentions
                preference_keywords = ["spicy", "mild", "hot", "cold", "sweet", "sour"]
                for keyword in preference_keywords:
                    if keyword in content_lower:
                        order_context["preferences"].append(keyword)
        
        # Remove duplicates
        for key in order_context:
            order_context[key] = list(set(order_context[key]))
        
        return order_context

class ConversationMemoryService:
    """Service for managing conversation memory across requests."""
    
    def __init__(self, session_timeout_minutes: int = 30):
        self.sessions: Dict[str, ConversationSession] = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self._lock = threading.Lock()
        logger.info(f"ConversationMemoryService initialized with {session_timeout_minutes}min timeout")

    def create_session(
        self, 
        session_id: str,
        business_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> ConversationSession:
        """Create a new conversation session."""
        with self._lock:
            session = ConversationSession(
                session_id=session_id,
                business_id=business_id,
                user_id=user_id,
                messages=[],
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                context={}
            )
            self.sessions[session_id] = session
            logger.info(f"Created new conversation session: {session_id}")
            return session

    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Get an existing conversation session."""
        with self._lock:
            session = self.sessions.get(session_id)
            if session:
                # Check if session has expired
                if datetime.utcnow() - session.last_activity > self.session_timeout:
                    logger.info(f"Session {session_id} expired, removing")
                    del self.sessions[session_id]
                    return None
                return session
            return None

    def get_or_create_session(
        self,
        session_id: str,
        business_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> ConversationSession:
        """Get existing session or create new one."""
        session = self.get_session(session_id)
        if session is None:
            session = self.create_session(session_id, business_id, user_id)
        return session

    def add_user_message(
        self,
        session_id: str,
        message: str,
        business_id: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConversationSession:
        """Add a user message to the conversation."""
        session = self.get_or_create_session(session_id, business_id, user_id)
        session.add_message("user", message, metadata)
        logger.debug(f"Added user message to session {session_id}")
        return session

    def add_assistant_message(
        self,
        session_id: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[ConversationSession]:
        """Add an assistant message to the conversation."""
        session = self.get_session(session_id)
        if session:
            session.add_message("assistant", message, metadata)
            logger.debug(f"Added assistant message to session {session_id}")
        return session

    def get_conversation_context(
        self,
        session_id: str,
        message_limit: int = 10
    ) -> str:
        """Get formatted conversation context for agents."""
        session = self.get_session(session_id)
        if session:
            return session.get_conversation_context(message_limit)
        return ""

    def get_order_context(self, session_id: str) -> Dict[str, Any]:
        """Get order-related context from the conversation."""
        session = self.get_session(session_id)
        if session:
            return session.extract_order_context()
        return {}

    def clear_session(self, session_id: str) -> bool:
        """Clear a conversation session."""
        with self._lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
                logger.info(f"Cleared session: {session_id}")
                return True
            return False

    def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        with self._lock:
            now = datetime.utcnow()
            expired_sessions = [
                session_id for session_id, session in self.sessions.items()
                if now - session.last_activity > self.session_timeout
            ]
            
            for session_id in expired_sessions:
                del self.sessions[session_id]
                logger.info(f"Cleaned up expired session: {session_id}")
            
            if expired_sessions:
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about active sessions."""
        with self._lock:
            return {
                "active_sessions": len(self.sessions),
                "sessions_by_business": defaultdict(int, {
                    session.business_id: sum(1 for s in self.sessions.values() if s.business_id == session.business_id)
                    for session in self.sessions.values() if session.business_id
                }),
                "total_messages": sum(len(session.messages) for session in self.sessions.values())
            }

# Global instance
conversation_memory = ConversationMemoryService()