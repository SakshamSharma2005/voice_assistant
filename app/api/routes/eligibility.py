from fastapi import APIRouter, HTTPException, status
import logging

from app.models.user import (
    EligibilityCheckRequest, EligibilityCheckResponse,
    UserProfile
)
from app.services.scheme_service import scheme_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/check", response_model=EligibilityCheckResponse)
async def check_eligibility(request: EligibilityCheckRequest):
    """
    Check user eligibility for government schemes
    
    Analyzes user profile against all schemes or specific scheme IDs
    Returns detailed eligibility results with match percentages,
    missing criteria, required documents, and recommendations
    """
    try:
        result = await scheme_service.check_eligibility(request)
        
        logger.info(
            f"Eligibility check completed: {result.eligible_schemes_count}/"
            f"{result.total_schemes_checked} eligible"
        )
        return result
        
    except Exception as e:
        logger.error(f"Eligibility check error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check eligibility: {str(e)}"
        )


@router.post("/quick-check")
async def quick_eligibility_check(profile: UserProfile):
    """
    Quick eligibility check for top schemes
    
    Simplified endpoint that returns only high-priority eligible schemes
    Useful for initial screening and quick recommendations
    """
    try:
        # Check eligibility for all schemes
        request = EligibilityCheckRequest(
            user_profile=profile,
            include_state_schemes=True
        )
        
        result = await scheme_service.check_eligibility(request)
        
        # Filter only high-priority eligible schemes
        top_schemes = [
            r for r in result.results
            if r.is_eligible and r.priority == "high"
        ][:5]
        
        return {
            "success": True,
            "eligible_schemes_count": len(top_schemes),
            "top_schemes": top_schemes,
            "recommendations": result.recommendations[:3],
            "next_steps": result.next_steps[:3]
        }
        
    except Exception as e:
        logger.error(f"Quick eligibility check error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform quick check: {str(e)}"
        )
