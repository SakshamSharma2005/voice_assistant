"""
Input validation utilities
"""
import re
from typing import Optional


def validate_phone_number(phone: str) -> bool:
    """Validate Indian phone number"""
    pattern = r'^[6-9]\d{9}$'
    return bool(re.match(pattern, phone.replace('+91', '').replace(' ', '').replace('-', '')))


def validate_aadhaar(aadhaar: str) -> bool:
    """Validate Aadhaar number format"""
    aadhaar = aadhaar.replace(' ', '').replace('-', '')
    pattern = r'^\d{12}$'
    return bool(re.match(pattern, aadhaar))


def validate_pan(pan: str) -> bool:
    """Validate PAN card format"""
    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    return bool(re.match(pattern, pan.upper()))


def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
    """Sanitize text input"""
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text.strip()


def validate_age(age: int) -> bool:
    """Validate age"""
    return 0 <= age <= 120


def validate_income(income: int) -> bool:
    """Validate annual income"""
    return 0 <= income <= 100000000  # Max 10 crore
