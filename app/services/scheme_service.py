"""
Scheme Service - Business logic for scheme operations
Handles scheme search, matching, and eligibility calculations
"""
import json
import logging
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime

from app.config import settings
from app.models.scheme import (
    Scheme, SchemeSearchCriteria, SchemeSearchResponse,
    SchemeCategory, EligibilityCriteria
)
from app.models.user import (
    UserProfile, EligibilityCheckRequest, EligibilityCheckResponse,
    EligibilityResult
)

logger = logging.getLogger(__name__)


class SchemeService:
    """Service for scheme-related operations"""
    
    def __init__(self):
        self.schemes: List[Scheme] = []
        self.schemes_by_id: Dict[str, Scheme] = {}
        self._load_schemes()
        logger.info(f"Scheme service initialized with {len(self.schemes)} schemes")
    
    def _load_schemes(self):
        """Load schemes from JSON database"""
        try:
            schemes_file = Path("app/data/schemes.json")
            if not schemes_file.exists():
                logger.warning("Schemes database file not found")
                return
            
            with open(schemes_file, 'r', encoding='utf-8') as f:
                schemes_data = json.load(f)
            
            for scheme_data in schemes_data:
                try:
                    scheme = Scheme(**scheme_data)
                    self.schemes.append(scheme)
                    self.schemes_by_id[scheme.scheme_id] = scheme
                except Exception as e:
                    logger.error(f"Error loading scheme {scheme_data.get('scheme_id')}: {str(e)}")
            
            logger.info(f"Loaded {len(self.schemes)} schemes successfully")
            
        except Exception as e:
            logger.error(f"Error loading schemes database: {str(e)}")
    
    async def search_schemes(
        self,
        criteria: SchemeSearchCriteria,
        limit: int = 20
    ) -> SchemeSearchResponse:
        """
        Search schemes based on criteria
        
        Args:
            criteria: Search criteria
            limit: Maximum number of results
            
        Returns:
            SchemeSearchResponse with matched schemes and scores
        """
        try:
            matched_schemes = []
            match_scores = {}
            
            for scheme in self.schemes:
                if not scheme.is_active:
                    continue
                
                score = self._calculate_match_score(scheme, criteria)
                
                if score > 0:
                    matched_schemes.append((scheme, score))
                    match_scores[scheme.scheme_id] = score
            
            # Sort by score descending
            matched_schemes.sort(key=lambda x: x[1], reverse=True)
            
            # Get top N schemes
            top_schemes = [scheme for scheme, _ in matched_schemes[:limit]]
            
            logger.info(f"Found {len(top_schemes)} schemes matching criteria")
            
            return SchemeSearchResponse(
                total=len(top_schemes),
                schemes=top_schemes,
                match_scores=match_scores
            )
            
        except Exception as e:
            logger.error(f"Error searching schemes: {str(e)}")
            return SchemeSearchResponse(total=0, schemes=[])
    
    def _calculate_match_score(
        self,
        scheme: Scheme,
        criteria: SchemeSearchCriteria
    ) -> float:
        """Calculate relevance score for a scheme"""
        score = 0.0
        max_score = 0.0
        
        eligibility = scheme.eligibility
        
        # Age matching (weight: 20)
        if criteria.age is not None:
            max_score += 20
            if eligibility.age_min is not None and criteria.age < eligibility.age_min:
                pass  # Not eligible
            elif eligibility.age_max is not None and criteria.age > eligibility.age_max:
                pass  # Not eligible
            else:
                score += 20  # Age matches
        
        # Income matching (weight: 15)
        if criteria.income is not None:
            max_score += 15
            if eligibility.income_limit is None or criteria.income <= eligibility.income_limit:
                score += 15
        
        # Occupation matching (weight: 25)
        if criteria.occupation:
            max_score += 25
            if eligibility.occupation:
                if criteria.occupation.lower() in [occ.lower() for occ in eligibility.occupation]:
                    score += 25
        
        # State matching (weight: 15)
        if criteria.state:
            max_score += 15
            if eligibility.states:
                if "all" in eligibility.states or criteria.state in eligibility.states:
                    score += 15
        
        # Category matching (weight: 15)
        if criteria.category:
            max_score += 15
            for cat in criteria.category:
                if cat in scheme.category:
                    score += 15 / len(criteria.category)
        
        # Gender matching (weight: 5)
        if criteria.gender:
            max_score += 5
            if eligibility.gender in [None, "Any", criteria.gender]:
                score += 5
        
        # BPL card matching (weight: 5)
        if criteria.has_bpl_card is not None:
            max_score += 5
            if eligibility.bpl_card is None or eligibility.bpl_card == criteria.has_bpl_card:
                score += 5
        
        # Keyword matching (bonus points)
        if criteria.keywords:
            keywords_lower = criteria.keywords.lower()
            scheme_text = f"{scheme.name.en} {scheme.description.en}".lower()
            if any(word in scheme_text for word in keywords_lower.split()):
                score += 10
        
        # Normalize score to 0-100
        if max_score > 0:
            return min(100, (score / max_score) * 100)
        return 0
    
    async def get_scheme_by_id(self, scheme_id: str) -> Optional[Scheme]:
        """Get scheme by ID"""
        return self.schemes_by_id.get(scheme_id)
    
    async def check_eligibility(
        self,
        request: EligibilityCheckRequest
    ) -> EligibilityCheckResponse:
        """
        Check user eligibility for schemes
        
        Args:
            request: Eligibility check request with user profile
            
        Returns:
            EligibilityCheckResponse with results for each scheme
        """
        try:
            profile = request.user_profile
            results = []
            
            # Determine which schemes to check
            schemes_to_check = []
            if request.scheme_ids:
                schemes_to_check = [
                    self.schemes_by_id[sid] for sid in request.scheme_ids
                    if sid in self.schemes_by_id
                ]
            else:
                schemes_to_check = [s for s in self.schemes if s.is_active]
            
            # Check eligibility for each scheme
            for scheme in schemes_to_check:
                result = await self._check_scheme_eligibility(scheme, profile)
                if result.match_percentage > 0:  # Only include if any match
                    results.append(result)
            
            # Sort by match percentage
            results.sort(key=lambda x: x.match_percentage, reverse=True)
            
            # Count eligible schemes (>= 70% match)
            eligible_count = sum(1 for r in results if r.is_eligible)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(results, profile)
            next_steps = self._generate_next_steps(results[:3], profile)
            
            logger.info(f"Checked eligibility: {eligible_count}/{len(results)} schemes eligible")
            
            return EligibilityCheckResponse(
                user_id=profile.user_id,
                total_schemes_checked=len(results),
                eligible_schemes_count=eligible_count,
                results=results,
                recommendations=recommendations,
                next_steps=next_steps
            )
            
        except Exception as e:
            logger.error(f"Error checking eligibility: {str(e)}")
            return EligibilityCheckResponse(
                total_schemes_checked=0,
                eligible_schemes_count=0,
                results=[]
            )
    
    async def _check_scheme_eligibility(
        self,
        scheme: Scheme,
        profile: UserProfile
    ) -> EligibilityResult:
        """Check if user is eligible for a specific scheme"""
        
        eligibility = scheme.eligibility
        matched = []
        missing = []
        missing_docs = []
        
        total_criteria = 0
        matched_criteria = 0
        
        # Age check
        total_criteria += 1
        if eligibility.age_min is not None:
            if profile.age >= eligibility.age_min:
                if eligibility.age_max is None or profile.age <= eligibility.age_max:
                    matched.append("age")
                    matched_criteria += 1
                else:
                    missing.append(f"age (must be ≤ {eligibility.age_max})")
            else:
                missing.append(f"age (must be ≥ {eligibility.age_min})")
        else:
            matched.append("age")
            matched_criteria += 1
        
        # Occupation check
        if eligibility.occupation:
            total_criteria += 1
            if profile.occupation.value in eligibility.occupation:
                matched.append("occupation")
                matched_criteria += 1
            else:
                missing.append(f"occupation (requires: {', '.join(eligibility.occupation)})")
        
        # Income check
        if eligibility.income_limit is not None:
            total_criteria += 1
            if profile.annual_income and profile.annual_income <= eligibility.income_limit:
                matched.append("income")
                matched_criteria += 1
            elif profile.annual_income:
                missing.append(f"income (must be ≤ ₹{eligibility.income_limit})")
        
        # State check
        if eligibility.states and "all" not in eligibility.states:
            total_criteria += 1
            if profile.state in eligibility.states:
                matched.append("location")
                matched_criteria += 1
            else:
                missing.append(f"location (only for: {', '.join(eligibility.states)})")
        
        # Gender check
        if eligibility.gender and eligibility.gender != "Any":
            total_criteria += 1
            if profile.gender.value == eligibility.gender.lower():
                matched.append("gender")
                matched_criteria += 1
            else:
                missing.append(f"gender (requires: {eligibility.gender})")
        
        # BPL card check
        if eligibility.bpl_card is True:
            total_criteria += 1
            if profile.has_bpl_card:
                matched.append("BPL card")
                matched_criteria += 1
            else:
                missing.append("BPL card")
        
        # Land ownership check
        if eligibility.land_ownership is True:
            total_criteria += 1
            if profile.is_farmer and profile.land_size_acres and profile.land_size_acres > 0:
                matched.append("land ownership")
                matched_criteria += 1
            else:
                missing.append("land ownership")
        
        # Bank account check
        if eligibility.bank_account is True:
            total_criteria += 1
            if profile.has_bank_account:
                matched.append("bank account")
                matched_criteria += 1
            else:
                missing_docs.append("bank account")
        
        # Document checks
        for doc in scheme.documents_required:
            if doc == "aadhaar" and not profile.has_aadhaar:
                missing_docs.append("Aadhaar card")
            elif doc == "pan_card" and not profile.has_pan:
                missing_docs.append("PAN card")
            elif doc == "bank_account" and not profile.has_bank_account:
                if "bank account" not in missing_docs:
                    missing_docs.append("bank account")
        
        # Calculate match percentage
        match_percentage = (matched_criteria / total_criteria * 100) if total_criteria > 0 else 0
        
        # Determine eligibility (70% threshold)
        is_eligible = match_percentage >= 70 and len(missing) == 0
        
        # Generate recommendation
        if is_eligible:
            if missing_docs:
                recommendation = f"You are eligible! Arrange these documents: {', '.join(missing_docs)}"
            else:
                recommendation = "You are eligible! You can apply now."
        elif match_percentage >= 50:
            recommendation = f"Partially eligible. Missing: {', '.join(missing[:2])}"
        else:
            recommendation = "Not eligible for this scheme"
        
        # Determine priority
        if match_percentage >= 90:
            priority = "high"
        elif match_percentage >= 70:
            priority = "medium"
        else:
            priority = "low"
        
        return EligibilityResult(
            scheme_id=scheme.scheme_id,
            scheme_name=scheme.name.en,
            is_eligible=is_eligible,
            match_percentage=round(match_percentage, 1),
            matched_criteria=matched,
            missing_criteria=missing,
            missing_documents=missing_docs,
            recommendation=recommendation,
            priority=priority
        )
    
    def _generate_recommendations(
        self,
        results: List[EligibilityResult],
        profile: UserProfile
    ) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        eligible = [r for r in results if r.is_eligible]
        high_priority = [r for r in results if r.priority == "high"]
        
        if eligible:
            recommendations.append(
                f"You are eligible for {len(eligible)} government schemes!"
            )
            
            if high_priority:
                top_scheme = high_priority[0]
                recommendations.append(
                    f"{top_scheme.scheme_name} is highly recommended for you"
                )
        else:
            recommendations.append(
                "You don't fully match any schemes yet, but here are close matches"
            )
        
        # Document recommendations
        missing_docs = set()
        for result in results[:5]:
            missing_docs.update(result.missing_documents)
        
        if missing_docs:
            recommendations.append(
                f"Arrange these documents to improve eligibility: {', '.join(list(missing_docs)[:3])}"
            )
        
        return recommendations
    
    def _generate_next_steps(
        self,
        top_results: List[EligibilityResult],
        profile: UserProfile
    ) -> List[str]:
        """Generate actionable next steps"""
        steps = []
        
        for result in top_results:
            if result.is_eligible:
                steps.append(f"Apply for {result.scheme_name}")
            elif result.match_percentage >= 50:
                if result.missing_documents:
                    steps.append(
                        f"Get {result.missing_documents[0]} to qualify for {result.scheme_name}"
                    )
        
        if not steps:
            steps.append("Visit nearest CSC center for personalized guidance")
            steps.append("Call national helpline: 1800-XXX-XXXX")
        
        return steps[:5]  # Max 5 steps
    
    async def get_schemes_by_category(
        self,
        category: SchemeCategory,
        limit: int = 10
    ) -> List[Scheme]:
        """Get schemes by category"""
        schemes = [
            s for s in self.schemes
            if s.is_active and category in s.category
        ]
        return schemes[:limit]


# Singleton instance
scheme_service = SchemeService()
