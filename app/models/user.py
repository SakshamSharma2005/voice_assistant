from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class Gender(str, Enum):
    """Gender options"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class MaritalStatus(str, Enum):
    """Marital status options"""
    SINGLE = "single"
    MARRIED = "married"
    WIDOWED = "widowed"
    DIVORCED = "divorced"
    SEPARATED = "separated"


class OccupationType(str, Enum):
    """Occupation types"""
    FARMER = "farmer"
    LABORER = "laborer"
    STUDENT = "student"
    UNEMPLOYED = "unemployed"
    SELF_EMPLOYED = "self_employed"
    GOVERNMENT_EMPLOYEE = "government_employee"
    PRIVATE_EMPLOYEE = "private_employee"
    RETIRED = "retired"
    HOMEMAKER = "homemaker"
    OTHER = "other"


class UserProfile(BaseModel):
    """User profile for eligibility checking"""
    user_id: Optional[str] = Field(None, description="Unique user identifier")
    age: int = Field(..., ge=0, le=120, description="User age")
    gender: Gender
    state: str = Field(..., description="State of residence")
    district: Optional[str] = Field(None, description="District")
    occupation: OccupationType
    annual_income: Optional[int] = Field(None, ge=0, description="Annual income in INR")
    education: Optional[str] = Field(None, description="Highest education level")
    marital_status: Optional[MaritalStatus] = None
    category: Optional[str] = Field(None, description="Caste category (General/SC/ST/OBC)")
    
    # Document availability
    has_aadhaar: bool = Field(default=False)
    has_pan: bool = Field(default=False)
    has_bank_account: bool = Field(default=False)
    has_bpl_card: bool = Field(default=False)
    has_ration_card: bool = Field(default=False)
    
    # Specific conditions
    has_disability: bool = Field(default=False)
    disability_percentage: Optional[int] = Field(None, ge=0, le=100)
    is_farmer: bool = Field(default=False)
    land_size_acres: Optional[float] = Field(None, ge=0, description="Land ownership in acres")
    
    # Preferences
    preferred_language: str = Field(default="hi", description="Preferred language code")
    phone_number: Optional[str] = Field(None, description="Contact number")
    email: Optional[EmailStr] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "age": 45,
                "gender": "male",
                "state": "Uttar Pradesh",
                "occupation": "farmer",
                "annual_income": 150000,
                "education": "10th",
                "is_farmer": True,
                "land_size_acres": 2.5,
                "has_aadhaar": True,
                "has_bank_account": True,
                "preferred_language": "hi"
            }
        }


class EligibilityCheckRequest(BaseModel):
    """Request for checking scheme eligibility"""
    user_profile: UserProfile
    scheme_ids: Optional[list[str]] = Field(None, description="Specific schemes to check")
    include_state_schemes: bool = Field(default=True)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_profile": {
                    "age": 45,
                    "gender": "male",
                    "state": "Uttar Pradesh",
                    "occupation": "farmer"
                }
            }
        }


class EligibilityResult(BaseModel):
    """Result of eligibility check for a single scheme"""
    scheme_id: str
    scheme_name: str
    is_eligible: bool
    match_percentage: float = Field(..., ge=0, le=100, description="Match percentage")
    matched_criteria: list[str] = Field(default_factory=list)
    missing_criteria: list[str] = Field(default_factory=list)
    missing_documents: list[str] = Field(default_factory=list)
    recommendation: str = Field(..., description="Action recommendation")
    priority: str = Field(..., description="Priority level (high/medium/low)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "scheme_id": "PM-KISAN-001",
                "scheme_name": "PM Kisan Samman Nidhi",
                "is_eligible": True,
                "match_percentage": 95.0,
                "matched_criteria": ["age", "occupation", "location"],
                "missing_criteria": [],
                "missing_documents": ["land_records"],
                "recommendation": "Apply now - you meet all major criteria",
                "priority": "high"
            }
        }


class EligibilityCheckResponse(BaseModel):
    """Response for eligibility check"""
    user_id: Optional[str] = None
    total_schemes_checked: int
    eligible_schemes_count: int
    results: list[EligibilityResult]
    recommendations: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_schemes_checked": 50,
                "eligible_schemes_count": 8,
                "results": [],
                "recommendations": [
                    "You are eligible for 8 government schemes",
                    "PM Kisan is the highest priority for you"
                ]
            }
        }
