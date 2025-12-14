from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class AudioFormat(str, Enum):
    """Supported audio formats"""
    WAV = "wav"
    MP3 = "mp3"
    WEBM = "webm"
    OGG = "ogg"


class VoiceGender(str, Enum):
    """Voice gender options for TTS"""
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


class TranscribeRequest(BaseModel):
    """Request for speech-to-text transcription"""
    audio_base64: Optional[str] = Field(None, description="Base64 encoded audio data")
    audio_url: Optional[str] = Field(None, description="URL of audio file")
    audio_format: AudioFormat = Field(default=AudioFormat.MP3)
    language: Optional[str] = Field(None, description="Expected language (auto-detect if not provided)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "audio_base64": "UklGRiQAAABXQVZFZm10...",
                "audio_format": "mp3",
                "language": "hi"
            }
        }


class TranscribeResponse(BaseModel):
    """Response for speech-to-text transcription"""
    success: bool = True
    text: str = Field(..., description="Transcribed text")
    language: str = Field(..., description="Detected language")
    confidence: float = Field(..., ge=0, le=1, description="Transcription confidence")
    duration_seconds: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "text": "मुझे किसानों के लिए योजना बताओ",
                "language": "hi",
                "confidence": 0.95,
                "duration_seconds": 3.5
            }
        }


class SynthesizeRequest(BaseModel):
    """Request for text-to-speech synthesis"""
    text: str = Field(..., description="Text to synthesize", max_length=5000)
    language: str = Field(default="hi", description="Target language")
    voice_gender: VoiceGender = Field(default=VoiceGender.FEMALE)
    speech_rate: float = Field(default=1.0, ge=0.25, le=4.0, description="Speech rate multiplier")
    pitch: float = Field(default=0.0, ge=-20.0, le=20.0, description="Voice pitch adjustment")
    output_format: AudioFormat = Field(default=AudioFormat.MP3)
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "आपके लिए तीन योजनाएं मिली हैं",
                "language": "hi",
                "voice_gender": "female",
                "speech_rate": 0.9
            }
        }


class SynthesizeResponse(BaseModel):
    """Response for text-to-speech synthesis"""
    success: bool = True
    audio_url: str = Field(..., description="URL of generated audio file")
    audio_base64: Optional[str] = Field(None, description="Base64 encoded audio (if requested)")
    duration_seconds: float
    format: AudioFormat
    size_bytes: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "audio_url": "https://api.../audio/synth_abc123.mp3",
                "duration_seconds": 4.2,
                "format": "mp3",
                "size_bytes": 67584
            }
        }
