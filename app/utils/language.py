"""
Language detection and translation utilities
"""
from langdetect import detect, LangDetectException
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Language code mappings
LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "or": "Odia"
}

LANGUAGE_CODES = {
    "eng": "en",
    "hin": "hi",
    "tam": "ta",
    "tel": "te",
    "ben": "bn",
    "mar": "mr",
    "guj": "gu",
    "kan": "kn",
    "mal": "ml",
    "pan": "pa",
    "ori": "or"
}


def detect_language(text: str) -> Optional[str]:
    """
    Detect language from text
    
    Args:
        text: Text to analyze
        
    Returns:
        Language code or None if detection fails
    """
    try:
        detected = detect(text)
        # Map to our supported language codes
        return LANGUAGE_CODES.get(detected, detected)
    except LangDetectException:
        logger.warning(f"Failed to detect language for text: {text[:50]}")
        return None


def get_language_name(code: str) -> str:
    """Get language name from code"""
    return LANGUAGE_NAMES.get(code, code)


def is_supported_language(code: str) -> bool:
    """Check if language is supported"""
    return code in LANGUAGE_NAMES


def normalize_language_code(code: str) -> str:
    """Normalize language code to standard format"""
    code = code.lower().strip()
    
    # Handle ISO 639-2 codes
    if len(code) == 3:
        return LANGUAGE_CODES.get(code, code[:2])
    
    # Return as-is if already 2-letter code
    return code
