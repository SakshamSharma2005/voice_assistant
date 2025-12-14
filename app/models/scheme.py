from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum


class LanguageCode(str, Enum):
    """Supported language codes"""
    ENGLISH = "en"
    HINDI = "hi"
    TAMIL = "ta"
    TELUGU = "te"
    BENGALI = "bn"
    MARATHI = "mr"
    GUJARATI = "gu"
    KANNADA = "kn"
    MALAYALAM = "ml"
    PUNJABI = "pa"
    ODIA = "or"


class SchemeCategory(str, Enum):
    """Government scheme categories"""
    AGRICULTURE = "agriculture"
    EDUCATION = "education"
    HEALTHCARE = "healthcare"
    HOUSING = "housing"
    EMPLOYMENT = "employment"
    WOMEN_WELFARE = "women_welfare"
    SENIOR_CITIZEN = "senior_citizen"
    DISABILITY = "disability"
    FINANCIAL_INCLUSION = "financial_inclusion"
    SKILL_DEVELOPMENT = "skill_development"
    SOCIAL_SECURITY = "social_security"
    ENTREPRENEURSHIP = "entrepreneurship"


class BenefitType(str, Enum):
    """Types of scheme benefits"""
    DIRECT_TRANSFER = "direct_transfer"
    SUBSIDY = "subsidy"
    LOAN = "loan"
    INSURANCE = "insurance"
    TRAINING = "training"
    INFRASTRUCTURE = "infrastructure"
    SERVICE = "service"


class MultilingualText(BaseModel):
    """Multilingual text content"""
    en: str = Field(..., description="English text")
    hi: Optional[str] = Field(None, description="Hindi text")
    ta: Optional[str] = Field(None, description="Tamil text")
    te: Optional[str] = Field(None, description="Telugu text")
    bn: Optional[str] = Field(None, description="Bengali text")
    mr: Optional[str] = Field(None, description="Marathi text")
    gu: Optional[str] = Field(None, description="Gujarati text")
    kn: Optional[str] = Field(None, description="Kannada text")
    ml: Optional[str] = Field(None, description="Malayalam text")
    pa: Optional[str] = Field(None, description="Punjabi text")
    or_: Optional[str] = Field(None, alias="or", description="Odia text")
    
    def get_text(self, lang: str) -> str:
        """Get text in specified language, fallback to English"""
        return getattr(self, lang, None) or self.en


class EligibilityCriteria(BaseModel):
    """Eligibility criteria for a scheme"""
    age_min: Optional[int] = Field(None, description="Minimum age requirement")
    age_max: Optional[int] = Field(None, description="Maximum age requirement")
    income_limit: Optional[int] = Field(None, description="Maximum annual income in INR")
    occupation: Optional[List[str]] = Field(None, description="Required occupations")
    gender: Optional[str] = Field(None, description="Gender requirement (M/F/Other/Any)")
    category: Optional[List[str]] = Field(None, description="Caste category (General/SC/ST/OBC)")
    states: Optional[List[str]] = Field(None, description="Applicable states (or 'all')")
    land_ownership: Optional[bool] = Field(None, description="Requires land ownership")
    education: Optional[str] = Field(None, description="Minimum education requirement")
    marital_status: Optional[str] = Field(None, description="Marital status requirement")
    disability: Optional[bool] = Field(None, description="For persons with disabilities")
    bpl_card: Optional[bool] = Field(None, description="Requires Below Poverty Line card")
    ration_card: Optional[str] = Field(None, description="Ration card type required")
    bank_account: Optional[bool] = Field(True, description="Requires bank account")
    
    class Config:
        json_schema_extra = {
            "example": {
                "age_min": 18,
                "age_max": 60,
                "income_limit": 200000,
                "occupation": ["farmer"],
                "states": ["all"],
                "bank_account": True
            }
        }


class SchemeBenefits(BaseModel):
    """Benefits provided by a scheme"""
    amount: Optional[int] = Field(None, description="Benefit amount in INR")
    frequency: Optional[str] = Field(None, description="Payment frequency (monthly/yearly/one-time)")
    type: BenefitType = Field(..., description="Type of benefit")
    description: MultilingualText = Field(..., description="Benefit description")
    duration: Optional[str] = Field(None, description="Benefit duration")
    additional_benefits: Optional[List[str]] = Field(None, description="Additional benefits")


class ApplicationProcess(BaseModel):
    """Application process steps"""
    step_number: int
    description: MultilingualText
    online: bool = Field(default=False, description="Can be done online")
    required_documents: Optional[List[str]] = None


class Scheme(BaseModel):
    """Complete government scheme model"""
    scheme_id: str = Field(..., description="Unique scheme identifier")
    name: MultilingualText = Field(..., description="Scheme name")
    description: MultilingualText = Field(..., description="Scheme description")
    ministry: str = Field(..., description="Responsible ministry/department")
    category: List[SchemeCategory] = Field(..., description="Scheme categories")
    eligibility: EligibilityCriteria = Field(..., description="Eligibility criteria")
    benefits: SchemeBenefits = Field(..., description="Scheme benefits")
    documents_required: List[str] = Field(..., description="Required documents")
    application_process: List[ApplicationProcess] = Field(..., description="Application steps")
    helpline: Optional[str] = Field(None, description="Helpline number")
    website: Optional[str] = Field(None, description="Official website")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True, description="Scheme is currently active")
    launch_date: Optional[str] = Field(None, description="Scheme launch date")
    state_specific: Optional[str] = Field(None, description="State name if state-specific")
    
    class Config:
        json_schema_extra = {
            "example": {
                "scheme_id": "PM-KISAN-001",
                "name": {
                    "en": "PM Kisan Samman Nidhi",
                    "hi": "पीएम किसान सम्मान निधि"
                },
                "ministry": "Ministry of Agriculture and Farmers Welfare",
                "category": ["agriculture", "financial_inclusion"],
                "eligibility": {
                    "age_min": 18,
                    "occupation": ["farmer"],
                    "states": ["all"]
                }
            }
        }


class SchemeSearchCriteria(BaseModel):
    """Search criteria for finding schemes"""
    age: Optional[int] = None
    income: Optional[int] = None
    occupation: Optional[str] = None
    state: Optional[str] = None
    category: Optional[List[SchemeCategory]] = None
    gender: Optional[str] = None
    education: Optional[str] = None
    has_bpl_card: Optional[bool] = None
    has_disability: Optional[bool] = None
    keywords: Optional[str] = Field(None, description="Search keywords")
    
    class Config:
        json_schema_extra = {
            "example": {
                "age": 45,
                "occupation": "farmer",
                "state": "Uttar Pradesh",
                "category": ["agriculture"]
            }
        }


class SchemeSearchResponse(BaseModel):
    """Response for scheme search"""
    total: int
    schemes: List[Scheme]
    match_scores: Optional[Dict[str, float]] = Field(None, description="Relevance scores")
