from fastapi import APIRouter, HTTPException, status
import logging

from app.models.conversation import (
    SessionStartRequest, SessionStartResponse,
    Session
)
from app.services.session_service import session_service
from app.services.speech_service import speech_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/start", response_model=SessionStartResponse)
async def start_session(request: SessionStartRequest):
    """
    Start a new conversation session
    
    Creates a session with specified language and context
    Returns session ID and greeting message with optional audio
    """
    try:
        # Create session
        session = await session_service.create_session(
            language=request.language,
            user_id=request.user_id,
            user_context=request.user_context
        )
        
        # Generate greeting message
        greetings = {
            "hi": "नमस्ते! मैं सहायक हूं। मैं आपको सरकारी योजनाओं के बारे में जानकारी देने में मदद करूंगा। आप मुझसे क्या जानना चाहते हैं?",
            "en": "Hello! I am Sahayak. I will help you with information about government schemes. What would you like to know?",
            "ta": "வணக்கம்! நான் சகாயக். அரசு திட்டங்கள் பற்றிய தகவல்களில் உங்களுக்கு உதவுவேன். நீங்கள் என்ன தெரிந்து கொள்ள விரும்புகிறீர்கள்?",
            "te": "నమస్కారం! నేను సహాయక్. ప్రభుత్వ పథకాల గురించి మీకు సమాచారం అందించడంలో సహాయం చేస్తాను. మీరు ఏమి తెలుసుకోవాలనుకుంటున్నారు?",
            "bn": "নমস্কার! আমি সহায়ক। সরকারি প্রকল্প সম্পর্কে তথ্যে আপনাকে সাহায্য করব। আপনি কী জানতে চান?",
            "mr": "नमस्कार! मी सहायक आहे. मी तुम्हाला सरकारी योजनांबद्दल माहिती देण्यात मदत करेन. तुम्हाला काय जाणून घ्यायचे आहे?"
        }
        
        greeting_text = greetings.get(request.language, greetings["hi"])
        
        # Generate greeting audio
        greeting_audio_url = None
        try:
            greeting_audio_url, _, _, _ = await speech_service.synthesize_speech(
                text=greeting_text,
                language=request.language,
                speech_rate=0.9
            )
        except Exception as e:
            logger.warning(f"Failed to generate greeting audio: {str(e)}")
        
        logger.info(f"Started session: {session.session_id}")
        
        return SessionStartResponse(
            session_id=session.session_id,
            expires_at=session.expires_at,
            greeting_message=greeting_text,
            greeting_audio_url=greeting_audio_url
        )
        
    except Exception as e:
        logger.error(f"Error starting session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start session: {str(e)}"
        )


@router.get("/{session_id}", response_model=Session)
async def get_session(session_id: str):
    """
    Get session details
    
    Returns session information including conversation history and context
    """
    try:
        session = await session_service.get_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session not found or expired: {session_id}"
            )
        
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session: {str(e)}"
        )


@router.delete("/{session_id}")
async def end_session(session_id: str):
    """
    End a conversation session
    
    Marks session as inactive and cleans up resources
    """
    try:
        success = await session_service.end_session(session_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session not found: {session_id}"
            )
        
        return {
            "success": True,
            "message": "Session ended successfully",
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end session: {str(e)}"
        )


@router.get("/{session_id}/history")
async def get_session_history(session_id: str, limit: int = 20):
    """
    Get conversation history for a session
    
    Returns list of messages with timestamps and metadata
    """
    try:
        history = await session_service.get_conversation_history(session_id, limit=limit)
        
        return {
            "success": True,
            "session_id": session_id,
            "message_count": len(history),
            "messages": history
        }
        
    except Exception as e:
        logger.error(f"Error getting session history {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session history: {str(e)}"
        )
