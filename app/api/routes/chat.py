from fastapi import APIRouter, HTTPException, status
import logging
import time
from typing import Optional

from app.models.conversation import (
    ChatQueryRequest, ChatQueryResponse, ChatResponseData,
    ResponseMetadata, Message, MessageRole, SuggestedAction
)
from app.services.gemini_service import gemini_service
from app.services.speech_service import speech_service
from app.services.session_service import session_service
from app.services.scheme_service import scheme_service
from app.models.scheme import SchemeSearchCriteria, SchemeCategory

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/query", response_model=ChatQueryResponse)
async def chat_query(request: ChatQueryRequest):
    """
    Process chat queries with AI-powered responses
    
    Handles natural language queries about government schemes,
    eligibility, applications, and provides intelligent responses
    with optional voice output
    """
    start_time = time.time()
    
    try:
        # Get or create session
        session = None
        if request.session_id:
            session = await session_service.get_session(request.session_id)
        
        if not session:
            # Create new session
            session = await session_service.create_session(
                language=request.language,
                user_context=request.user_context
            )
        
        # Build conversation history
        conversation_history = await session_service.get_conversation_history(
            session.session_id,
            limit=10
        )
        
        # Add user message to session
        user_message = Message(
            role=MessageRole.USER,
            content=request.query,
            language=request.language
        )
        await session_service.update_session(
            session.session_id,
            message=user_message
        )
        
        # Search for relevant schemes based on query
        available_schemes = await _find_relevant_schemes(
            query=request.query,
            user_context=request.user_context or {}
        )
        
        # Generate AI response
        ai_response = await gemini_service.generate_response(
            user_query=request.query,
            language=request.language,
            conversation_history=conversation_history,
            context=request.user_context or {},
            available_schemes=available_schemes
        )
        
        # Generate voice response if needed
        audio_url = None
        if request.voice_input or len(ai_response["response_text"]) < 500:
            try:
                audio_url, _, _, _ = await speech_service.synthesize_speech(
                    text=ai_response["response_text"],
                    language=request.language,
                    speech_rate=0.9  # Slightly slower for better comprehension
                )
            except Exception as e:
                logger.warning(f"Voice synthesis failed: {str(e)}")
        
        # Add assistant message to session
        assistant_message = Message(
            role=MessageRole.ASSISTANT,
            content=ai_response["response_text"],
            language=request.language,
            audio_url=audio_url
        )
        
        # Update session with response and context
        context_updates = {
            "current_intent": ai_response["intent"],
            "mentioned_schemes": [s.get("scheme_id") for s in available_schemes[:3]],
            "clarification_needed": ai_response["needs_clarification"]
        }
        
        await session_service.update_session(
            session.session_id,
            message=assistant_message,
            context_updates=context_updates
        )
        
        # Build suggested actions
        suggested_actions = []
        for action in ai_response["suggested_actions"]:
            suggested_actions.append(SuggestedAction(**action))
        
        # Prepare scheme data for response
        schemes_data = []
        for scheme in available_schemes[:5]:
            schemes_data.append({
                "scheme_id": scheme.get("scheme_id"),
                "name": scheme.get("name", {}).get(request.language, scheme.get("name", {}).get("en")),
                "description": scheme.get("description", {}).get(request.language, "")[:200],
                "helpline": scheme.get("helpline"),
                "website": scheme.get("website")
            })
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        # Build response
        response_data = ChatResponseData(
            response_text=ai_response["response_text"],
            response_audio_url=audio_url,
            language=request.language,
            schemes=schemes_data,
            suggested_actions=suggested_actions,
            session_id=session.session_id,
            intent=ai_response["intent"],
            needs_clarification=ai_response["needs_clarification"],
            clarification_question=ai_response.get("clarification_question")
        )
        
        metadata = ResponseMetadata(
            processing_time_ms=round(processing_time, 2),
            model_used="gemini-1.5-flash"
        )
        
        return ChatQueryResponse(
            success=True,
            data=response_data,
            metadata=metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat query error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}"
        )


async def _find_relevant_schemes(query: str, user_context: dict) -> list:
    """Find schemes relevant to user query and context"""
    try:
        # Build search criteria from context
        criteria = SchemeSearchCriteria()
        
        if "age" in user_context:
            criteria.age = user_context["age"]
        if "income" in user_context:
            criteria.income = user_context["income"]
        if "occupation" in user_context:
            criteria.occupation = user_context["occupation"]
        if "state" in user_context:
            criteria.state = user_context["state"]
        
        # Extract keywords from query
        criteria.keywords = query
        
        # Search schemes
        search_result = await scheme_service.search_schemes(criteria, limit=10)
        
        # Convert to dict format
        schemes_list = []
        for scheme in search_result.schemes:
            schemes_list.append(scheme.model_dump())
        
        return schemes_list
        
    except Exception as e:
        logger.error(f"Error finding relevant schemes: {str(e)}")
        return []
