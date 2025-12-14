from fastapi import APIRouter, HTTPException, status, Query
import logging
from typing import Optional

from app.models.scheme import (
    SchemeSearchCriteria, SchemeSearchResponse,
    Scheme, SchemeCategory
)
from app.services.scheme_service import scheme_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/search", response_model=SchemeSearchResponse)
async def search_schemes(criteria: SchemeSearchCriteria):
    """
    Search government schemes based on criteria
    
    Search by age, income, occupation, state, category, and keywords
    Returns ranked list of matching schemes with relevance scores
    """
    try:
        result = await scheme_service.search_schemes(criteria, limit=20)
        
        logger.info(f"Scheme search returned {result.total} results")
        return result
        
    except Exception as e:
        logger.error(f"Scheme search error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search schemes: {str(e)}"
        )


@router.get("/{scheme_id}", response_model=Scheme)
async def get_scheme_details(scheme_id: str):
    """
    Get detailed information about a specific scheme
    
    Returns complete scheme data including eligibility, benefits,
    application process, required documents, and helpline information
    """
    try:
        scheme = await scheme_service.get_scheme_by_id(scheme_id)
        
        if not scheme:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scheme not found: {scheme_id}"
            )
        
        logger.info(f"Retrieved scheme: {scheme_id}")
        return scheme
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scheme {scheme_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scheme details: {str(e)}"
        )


@router.get("/category/{category}", response_model=list[Scheme])
async def get_schemes_by_category(
    category: SchemeCategory,
    limit: int = Query(default=10, ge=1, le=50)
):
    """
    Get schemes by category
    
    Categories: agriculture, education, healthcare, housing, employment,
    women_welfare, senior_citizen, disability, financial_inclusion,
    skill_development, social_security, entrepreneurship
    """
    try:
        schemes = await scheme_service.get_schemes_by_category(category, limit=limit)
        
        logger.info(f"Retrieved {len(schemes)} schemes for category: {category}")
        return schemes
        
    except Exception as e:
        logger.error(f"Error getting schemes by category {category}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get schemes by category: {str(e)}"
        )


@router.get("/", response_model=list[Scheme])
async def list_all_schemes(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    active_only: bool = Query(default=True)
):
    """
    List all available schemes with pagination
    
    Use skip and limit for pagination
    Set active_only=false to include inactive schemes
    """
    try:
        all_schemes = scheme_service.schemes
        
        # Filter active schemes if requested
        if active_only:
            all_schemes = [s for s in all_schemes if s.is_active]
        
        # Apply pagination
        paginated = all_schemes[skip:skip + limit]
        
        logger.info(f"Listed {len(paginated)} schemes (skip={skip}, limit={limit})")
        return paginated
        
    except Exception as e:
        logger.error(f"Error listing schemes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list schemes: {str(e)}"
        )
