from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """Message role types"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationIntent(str, Enum):
    """Detected conversation intents"""
    SCHEME_DISCOVERY = "scheme_discovery"
    ELIGIBILITY_CHECK = "eligibility_check"
    APPLICATION_GUIDANCE = "application_guidance"
    DOCUMENT_ASSISTANCE = "document_assistance"
    STATUS_CHECK = "status_check"
    GENERAL_QUERY = "general_query"
    COMPLAINT = "complaint"


class Message(BaseModel):
    """Single conversation message"""
    role: MessageRole
    content: str
    language: str = Field(default="hi", description="Language of the message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    audio_url: Optional[str] = Field(None, description="URL of audio message")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ConversationContext(BaseModel):
    """Context maintained across conversation"""
    user_profile: Optional[Dict[str, Any]] = None
    current_intent: Optional[ConversationIntent] = None
    collected_information: Dict[str, Any] = Field(default_factory=dict)
    mentioned_schemes: List[str] = Field(default_factory=list)
    pending_questions: List[str] = Field(default_factory=list)
    last_topic: Optional[str] = None
    clarification_needed: bool = False


class Session(BaseModel):
    """Conversation session"""
    session_id: str = Field(..., description="Unique session identifier")
    user_id: Optional[str] = None
    language: str = Field(default="hi", description="Session language")
    messages: List[Message] = Field(default_factory=list)
    context: ConversationContext = Field(default_factory=ConversationContext)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    is_active: bool = Field(default=True)
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_abc123xyz",
                "language": "hi",
                "messages": [
                    {
                        "role": "user",
                        "content": "मुझे किसानों के लिए योजना बताओ",
                        "language": "hi"
                    }
                ],
                "is_active": True
            }
        }


class SessionStartRequest(BaseModel):
    """Request to start a new session"""
    user_id: Optional[str] = None
    language: str = Field(default="hi", description="Preferred language")
    user_context: Optional[Dict[str, Any]] = Field(None, description="Initial user context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "language": "hi",
                "user_context": {
                    "state": "Uttar Pradesh",
                    "occupation": "farmer"
                }
            }
        }


class SessionStartResponse(BaseModel):
    """Response when starting a session"""
    session_id: str
    expires_at: datetime
    greeting_message: str
    greeting_audio_url: Optional[str] = None


class ChatQueryRequest(BaseModel):
    """Request for chat query"""
    query: str = Field(..., description="User's query text")
    language: str = Field(default="hi", description="Query language")
    session_id: Optional[str] = Field(None, description="Existing session ID")
    user_context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    voice_input: bool = Field(default=False, description="Whether input was voice")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "मुझे किसानों के लिए कोई योजना बताओ",
                "language": "hi",
                "user_context": {
                    "state": "Uttar Pradesh",
                    "occupation": "farmer"
                }
            }
        }


class SuggestedAction(BaseModel):
    """Suggested next action for user"""
    action: str = Field(..., description="Action type")
    label: str = Field(..., description="Display label")
    scheme_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class ChatQueryResponse(BaseModel):
    """Response for chat query"""
    success: bool = True
    data: "ChatResponseData"
    metadata: "ResponseMetadata"
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "response_text": "आपके लिए 3 योजनाएं मिलीं...",
                    "response_audio_url": "https://api.../audio/resp_123.mp3",
                    "language": "hi",
                    "session_id": "sess_abc123"
                }
            }
        }


class ChatResponseData(BaseModel):
    """Chat response data"""
    response_text: str
    response_audio_url: Optional[str] = None
    language: str
    schemes: List[Dict[str, Any]] = Field(default_factory=list)
    suggested_actions: List[SuggestedAction] = Field(default_factory=list)
    session_id: str
    intent: Optional[ConversationIntent] = None
    needs_clarification: bool = False
    clarification_question: Optional[str] = None


class ResponseMetadata(BaseModel):
    """Response metadata"""
    processing_time_ms: float
    tokens_used: Optional[int] = None
    model_used: Optional[str] = None
    cache_hit: bool = False
