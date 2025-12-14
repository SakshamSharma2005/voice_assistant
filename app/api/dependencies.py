"""Shared dependencies for API routes"""
from typing import Optional
from fastapi import Header, HTTPException, status


async def get_session_id(x_session_id: Optional[str] = Header(None)) -> Optional[str]:
    """Extract session ID from headers"""
    return x_session_id


async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> bool:
    """Verify API key if authentication is enabled"""
    # Implement API key verification logic
    return True
