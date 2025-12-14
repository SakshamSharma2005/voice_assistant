"""
Speech Services - Text-to-Speech and Speech-to-Text
Uses Google gTTS for TTS (fallback to Google Cloud TTS if credentials available)
"""
import os
import io
import base64
import logging
import hashlib
from typing import Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor

from gtts import gTTS
from pydub import AudioSegment
import speech_recognition as sr

from app.config import settings
from app.models.voice import AudioFormat, VoiceGender

logger = logging.getLogger(__name__)

# Thread pool for blocking I/O operations
executor = ThreadPoolExecutor(max_workers=4)


class SpeechService:
    """Service for speech-to-text and text-to-speech operations"""
    
    def __init__(self):
        self.storage_path = Path(settings.AUDIO_STORAGE_PATH)
        self.temp_path = Path(settings.TEMP_AUDIO_PATH)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.temp_path.mkdir(parents=True, exist_ok=True)
        self.recognizer = sr.Recognizer()
        logger.info("Speech service initialized")
    
    async def transcribe_audio(
        self,
        audio_data: bytes,
        audio_format: AudioFormat,
        language: Optional[str] = None
    ) -> Tuple[str, str, float]:
        """
        Transcribe audio to text
        
        Args:
            audio_data: Audio file bytes
            audio_format: Audio format (wav, mp3, etc.)
            language: Expected language (None for auto-detect)
            
        Returns:
            Tuple of (transcribed_text, detected_language, confidence)
        """
        try:
            # Save audio to temp file
            temp_file = self.temp_path / f"temp_audio_{datetime.now().timestamp()}.{audio_format.value}"
            
            # Run blocking I/O in thread pool
            await asyncio.get_event_loop().run_in_executor(
                executor,
                lambda: temp_file.write_bytes(audio_data)
            )
            
            # Convert to WAV if needed
            wav_file = await self._convert_to_wav(temp_file, audio_format)
            
            # Perform speech recognition
            text, detected_lang, confidence = await self._recognize_speech(wav_file, language)
            
            # Cleanup temp files
            await self._cleanup_file(temp_file)
            if wav_file != temp_file:
                await self._cleanup_file(wav_file)
            
            logger.info(f"Transcribed audio: {text[:50]}... (lang: {detected_lang})")
            return text, detected_lang, confidence
            
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            raise Exception(f"Failed to transcribe audio: {str(e)}")
    
    async def synthesize_speech(
        self,
        text: str,
        language: str = "hi",
        voice_gender: VoiceGender = VoiceGender.FEMALE,
        speech_rate: float = 1.0,
        output_format: AudioFormat = AudioFormat.MP3
    ) -> Tuple[str, bytes, float, int]:
        """
        Convert text to speech
        
        Args:
            text: Text to convert
            language: Target language code
            voice_gender: Voice gender preference
            speech_rate: Speech rate multiplier
            output_format: Output audio format
            
        Returns:
            Tuple of (audio_url, audio_bytes, duration_seconds, size_bytes)
        """
        try:
            # Generate unique filename based on text hash
            text_hash = hashlib.md5(f"{text}{language}{speech_rate}".encode()).hexdigest()[:12]
            filename = f"tts_{text_hash}_{datetime.now().timestamp()}.{output_format.value}"
            output_path = self.storage_path / filename
            
            # Check if already cached
            if output_path.exists():
                logger.info(f"Using cached TTS audio: {filename}")
                audio_bytes = await asyncio.get_event_loop().run_in_executor(
                    executor,
                    lambda: output_path.read_bytes()
                )
            else:
                # Generate speech using gTTS
                audio_bytes = await self._generate_gtts(text, language, speech_rate)
                
                # Save to storage
                await asyncio.get_event_loop().run_in_executor(
                    executor,
                    lambda: output_path.write_bytes(audio_bytes)
                )
            
            # Calculate duration
            duration = await self._get_audio_duration(output_path)
            
            # Generate URL (in production, this would be a CDN URL)
            audio_url = f"/api/{settings.API_VERSION}/audio/{filename}"
            
            logger.info(f"Generated TTS audio: {filename} ({duration:.2f}s)")
            return audio_url, audio_bytes, duration, len(audio_bytes)
            
        except Exception as e:
            logger.error(f"Speech synthesis error: {str(e)}")
            raise Exception(f"Failed to synthesize speech: {str(e)}")
    
    async def _convert_to_wav(self, audio_file: Path, audio_format: AudioFormat) -> Path:
        """Convert audio file to WAV format"""
        if audio_format == AudioFormat.WAV:
            return audio_file
        
        try:
            wav_file = audio_file.with_suffix('.wav')
            
            def convert():
                audio = AudioSegment.from_file(str(audio_file), format=audio_format.value)
                audio.export(str(wav_file), format='wav')
            
            await asyncio.get_event_loop().run_in_executor(executor, convert)
            return wav_file
            
        except Exception as e:
            logger.error(f"Audio conversion error: {str(e)}")
            return audio_file  # Return original if conversion fails
    
    async def _recognize_speech(
        self,
        audio_file: Path,
        language: Optional[str]
    ) -> Tuple[str, str, float]:
        """Perform speech recognition on audio file"""
        
        def recognize():
            with sr.AudioFile(str(audio_file)) as source:
                audio = self.recognizer.record(source)
                
                # Map language codes to Google Speech Recognition format
                lang_map = {
                    "hi": "hi-IN",
                    "en": "en-IN",
                    "ta": "ta-IN",
                    "te": "te-IN",
                    "bn": "bn-IN",
                    "mr": "mr-IN",
                    "gu": "gu-IN",
                    "kn": "kn-IN",
                    "ml": "ml-IN",
                    "pa": "pa-IN",
                    "or": "or-IN"
                }
                
                # Try recognition with specified language or Hindi as default
                lang_code = lang_map.get(language, "hi-IN") if language else "hi-IN"
                
                try:
                    # Using Google Speech Recognition (free)
                    text = self.recognizer.recognize_google(audio, language=lang_code)
                    detected_lang = language or "hi"
                    confidence = 0.85  # Google doesn't provide confidence, use default
                    
                    return text, detected_lang, confidence
                    
                except sr.UnknownValueError:
                    # Try English if primary language fails
                    if lang_code != "en-IN":
                        text = self.recognizer.recognize_google(audio, language="en-IN")
                        return text, "en", 0.70
                    raise Exception("Speech not understood")
                    
                except sr.RequestError as e:
                    raise Exception(f"Speech recognition service error: {str(e)}")
        
        return await asyncio.get_event_loop().run_in_executor(executor, recognize)
    
    async def _generate_gtts(self, text: str, language: str, speed: float) -> bytes:
        """Generate speech using Google Text-to-Speech"""
        
        def generate():
            # Map language codes to gTTS format
            lang_map = {
                "hi": "hi",
                "en": "en",
                "ta": "ta",
                "te": "te",
                "bn": "bn",
                "mr": "mr",
                "gu": "gu",
                "kn": "kn",
                "ml": "ml",
                "pa": "pa",
                "or": "or"
            }
            
            gtts_lang = lang_map.get(language, "hi")
            
            # Generate speech
            tts = gTTS(text=text, lang=gtts_lang, slow=(speed < 0.9))
            
            # Save to bytes buffer
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            # Apply speed adjustment if needed (using pydub)
            if abs(speed - 1.0) > 0.1:
                audio = AudioSegment.from_file(audio_buffer, format="mp3")
                audio = audio.speedup(playback_speed=speed)
                
                output_buffer = io.BytesIO()
                audio.export(output_buffer, format="mp3")
                output_buffer.seek(0)
                return output_buffer.read()
            
            return audio_buffer.read()
        
        return await asyncio.get_event_loop().run_in_executor(executor, generate)
    
    async def _get_audio_duration(self, audio_file: Path) -> float:
        """Get duration of audio file in seconds"""
        try:
            def get_duration():
                audio = AudioSegment.from_file(str(audio_file))
                return len(audio) / 1000.0  # Convert ms to seconds
            
            return await asyncio.get_event_loop().run_in_executor(executor, get_duration)
        except Exception as e:
            logger.error(f"Error getting audio duration: {str(e)}")
            return 0.0
    
    async def _cleanup_file(self, file_path: Path):
        """Delete temporary file"""
        try:
            await asyncio.get_event_loop().run_in_executor(
                executor,
                lambda: file_path.unlink(missing_ok=True)
            )
        except Exception as e:
            logger.error(f"Error cleaning up file {file_path}: {str(e)}")
    
    async def cleanup_old_files(self):
        """Clean up audio files older than retention period"""
        try:
            retention_hours = settings.AUDIO_RETENTION_HOURS
            cutoff_time = datetime.now() - timedelta(hours=retention_hours)
            
            def cleanup():
                deleted = 0
                for file_path in self.storage_path.glob("*"):
                    if file_path.is_file():
                        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if file_time < cutoff_time:
                            file_path.unlink()
                            deleted += 1
                return deleted
            
            deleted = await asyncio.get_event_loop().run_in_executor(executor, cleanup)
            logger.info(f"Cleaned up {deleted} old audio files")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")


# Singleton instance
speech_service = SpeechService()
