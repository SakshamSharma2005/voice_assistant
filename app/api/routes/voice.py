from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse, Response
import base64
import logging
from pathlib import Path

from app.models.voice import (
    TranscribeRequest, TranscribeResponse,
    SynthesizeRequest, SynthesizeResponse,
    AudioFormat
)
from app.services.speech_service import speech_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(
    audio_file: UploadFile = File(None),
    audio_base64: str = None,
    audio_format: str = "mp3",
    language: str = None
):
    """
    Convert speech to text
    
    Accepts either:
    - audio_file: Uploaded audio file
    - audio_base64: Base64 encoded audio data
    
    Returns transcribed text with detected language and confidence
    """
    try:
        # Get audio data
        audio_data = None
        
        if audio_file:
            audio_data = await audio_file.read()
            # Detect format from filename if not provided
            if audio_file.filename:
                ext = Path(audio_file.filename).suffix.lower().replace('.', '')
                if ext in ['wav', 'mp3', 'webm', 'ogg']:
                    audio_format = ext
        elif audio_base64:
            try:
                audio_data = base64.b64decode(audio_base64)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid base64 audio data: {str(e)}"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either audio_file or audio_base64 must be provided"
            )
        
        # Validate format
        try:
            audio_fmt = AudioFormat(audio_format.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported audio format: {audio_format}"
            )
        
        # Transcribe
        text, detected_lang, confidence = await speech_service.transcribe_audio(
            audio_data=audio_data,
            audio_format=audio_fmt,
            language=language
        )
        
        return TranscribeResponse(
            success=True,
            text=text,
            language=detected_lang,
            confidence=confidence
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}"
        )


@router.post("/synthesize", response_model=SynthesizeResponse)
async def synthesize_speech(request: SynthesizeRequest):
    """
    Convert text to speech
    
    Generates audio from text in specified language with voice customization options
    """
    try:
        # Validate text length
        if len(request.text) > 5000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text exceeds maximum length of 5000 characters"
            )
        
        # Generate speech
        audio_url, audio_bytes, duration, size_bytes = await speech_service.synthesize_speech(
            text=request.text,
            language=request.language,
            voice_gender=request.voice_gender,
            speech_rate=request.speech_rate,
            output_format=request.output_format
        )
        
        return SynthesizeResponse(
            success=True,
            audio_url=audio_url,
            audio_base64=base64.b64encode(audio_bytes).decode('utf-8') if len(audio_bytes) < 500000 else None,
            duration_seconds=duration,
            format=request.output_format,
            size_bytes=size_bytes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Synthesis error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech synthesis failed: {str(e)}"
        )
