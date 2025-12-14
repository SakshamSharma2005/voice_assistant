"""
Google Gemini AI Service
Handles all interactions with Gemini API for intelligent conversations
"""
import google.generativeai as genai
from typing import List, Dict, Any, Optional
import json
import logging
from datetime import datetime

from app.config import settings
from app.models.conversation import Message, ConversationIntent

logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

# System prompt for the Sahayak assistant
SYSTEM_PROMPT = """
You are 'Sahayak' (सहायक), a friendly and helpful government scheme assistant for Indian citizens.

Your role:
1. Help users discover government schemes they're eligible for
2. Explain complex schemes in simple, everyday language
3. Guide users through application processes step-by-step
4. Answer in the user's preferred language (Hindi, English, or regional languages)
5. Be patient and ask one question at a time for low-literacy users

Key behaviors:
- Use simple words, avoid jargon and technical terms
- Give specific, actionable information
- Always mention helpline numbers when relevant
- If unsure, direct to nearest CSC (Common Service Center)
- Be empathetic to users' situations
- Keep responses conversational and warm

You have access to a database of 500+ central and state government schemes including:
- PM Kisan, PM Awas Yojana, Ayushman Bharat, MGNREGA
- State-specific schemes for each Indian state
- Schemes for farmers, women, elderly, students, SC/ST, OBC, minorities

When responding:
- Keep responses under 100 words for voice output
- Structure information clearly with bullet points when needed
- Offer to explain more if needed
- Be encouraging and positive
- Use local examples and relatable scenarios

Language guidelines:
- For Hindi: Use simple Hindustani, avoid pure Sanskrit words
- Mix English words that are commonly used (like "form", "apply", "document")
- For regional languages: Use conversational style

Important:
- Never make up scheme information - only use data provided
- Always verify eligibility before claiming user is eligible
- Prioritize schemes with highest relevance to user's profile
"""


class GeminiService:
    """Service for interacting with Google Gemini API"""
    
    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            generation_config={
                'temperature': 0.7,
                'top_p': 0.9,
                'top_k': 40,
                'max_output_tokens': 1024,
            }
        )
        logger.info("Gemini service initialized")
    
    async def generate_response(
        self,
        user_query: str,
        language: str,
        conversation_history: List[Message],
        context: Dict[str, Any],
        available_schemes: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate intelligent response using Gemini
        
        Args:
            user_query: User's question or query
            language: Preferred language code
            conversation_history: Previous messages in conversation
            context: Additional context (user profile, location, etc.)
            available_schemes: Relevant schemes data to provide context
            
        Returns:
            Dictionary with response text, intent, and suggested actions
        """
        try:
            # Build context for Gemini
            prompt = self._build_prompt(
                user_query=user_query,
                language=language,
                conversation_history=conversation_history,
                context=context,
                available_schemes=available_schemes
            )
            
            # Generate response
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Detect intent
            intent = self._detect_intent(user_query, response_text)
            
            # Extract suggested actions
            suggested_actions = self._extract_actions(response_text, available_schemes)
            
            # Check if clarification needed
            needs_clarification = self._needs_clarification(response_text)
            
            logger.info(f"Generated response for query in {language}: {user_query[:50]}...")
            
            return {
                "response_text": response_text,
                "intent": intent,
                "suggested_actions": suggested_actions,
                "needs_clarification": needs_clarification,
                "clarification_question": None  # Can be extracted from response if needed
            }
            
        except Exception as e:
            logger.error(f"Error generating Gemini response: {str(e)}")
            return {
                "response_text": self._get_fallback_response(language),
                "intent": ConversationIntent.GENERAL_QUERY,
                "suggested_actions": [],
                "needs_clarification": False
            }
    
    def _build_prompt(
        self,
        user_query: str,
        language: str,
        conversation_history: List[Message],
        context: Dict[str, Any],
        available_schemes: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Build comprehensive prompt for Gemini"""
        
        # Language instruction
        lang_instruction = {
            "hi": "Respond in simple Hindi (Hindustani) language.",
            "en": "Respond in simple English.",
            "ta": "Respond in Tamil language.",
            "te": "Respond in Telugu language.",
            "bn": "Respond in Bengali language.",
            "mr": "Respond in Marathi language.",
        }.get(language, "Respond in Hindi or English as appropriate.")
        
        # Build conversation history
        history_text = ""
        if conversation_history:
            history_text = "\n\nConversation History:\n"
            for msg in conversation_history[-5:]:  # Last 5 messages
                history_text += f"{msg.role.upper()}: {msg.content}\n"
        
        # Build context information
        context_text = "\n\nUser Context:\n"
        if context:
            for key, value in context.items():
                context_text += f"- {key}: {value}\n"
        
        # Build schemes information
        schemes_text = ""
        if available_schemes:
            schemes_text = "\n\nRelevant Government Schemes:\n"
            for scheme in available_schemes[:5]:  # Top 5 relevant schemes
                schemes_text += f"\n{scheme.get('name', {}).get(language, scheme.get('name', {}).get('en', 'Unknown'))}\n"
                schemes_text += f"  Description: {scheme.get('description', {}).get(language, scheme.get('description', {}).get('en', ''))[:150]}...\n"
                schemes_text += f"  Benefits: {scheme.get('benefits', {}).get('description', {}).get(language, '')}\n"
                schemes_text += f"  Helpline: {scheme.get('helpline', 'Not available')}\n"
        
        # Construct final prompt
        prompt = f"""{SYSTEM_PROMPT}

{lang_instruction}

{context_text}
{history_text}
{schemes_text}

Current User Query: {user_query}

Instructions:
- Answer the query directly and helpfully
- Keep response under 100 words
- Mention specific scheme names if relevant
- Include helpline numbers when applicable
- Be warm and encouraging

Your Response:"""
        
        return prompt
    
    def _detect_intent(self, user_query: str, response_text: str) -> ConversationIntent:
        """Detect conversation intent from query and response"""
        query_lower = user_query.lower()
        
        # Intent keywords mapping
        intent_keywords = {
            ConversationIntent.SCHEME_DISCOVERY: ["योजना", "scheme", "बताओ", "tell me", "कौन सी", "which", "मिल", "available"],
            ConversationIntent.ELIGIBILITY_CHECK: ["eligible", "पात्र", "मिलेगा", "can i get", "qualify", "योग्य"],
            ConversationIntent.APPLICATION_GUIDANCE: ["apply", "आवेदन", "कैसे करें", "how to", "process", "प्रक्रिया"],
            ConversationIntent.DOCUMENT_ASSISTANCE: ["document", "दस्तावेज", "certificate", "प्रमाण पत्र", "कागजात"],
            ConversationIntent.STATUS_CHECK: ["status", "स्थिति", "track", "पता करें", "check"],
            ConversationIntent.COMPLAINT: ["complaint", "शिकायत", "problem", "समस्या", "not working"],
        }
        
        # Check for intent keywords
        for intent, keywords in intent_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return intent
        
        return ConversationIntent.GENERAL_QUERY
    
    def _extract_actions(
        self,
        response_text: str,
        available_schemes: Optional[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Extract suggested actions from response"""
        actions = []
        
        # If schemes were mentioned, suggest checking eligibility
        if available_schemes:
            for scheme in available_schemes[:3]:
                actions.append({
                    "action": "check_eligibility",
                    "label": f"Check eligibility for {scheme.get('name', {}).get('en', 'scheme')}",
                    "scheme_id": scheme.get('scheme_id')
                })
        
        # Common actions based on response content
        response_lower = response_text.lower()
        
        if "apply" in response_lower or "आवेदन" in response_lower:
            actions.append({
                "action": "get_application_process",
                "label": "Get application process details"
            })
        
        if "document" in response_lower or "दस्तावेज" in response_lower:
            actions.append({
                "action": "get_documents",
                "label": "View required documents"
            })
        
        return actions[:3]  # Max 3 actions
    
    def _needs_clarification(self, response_text: str) -> bool:
        """Check if response indicates need for clarification"""
        clarification_keywords = [
            "can you tell me",
            "could you provide",
            "what is your",
            "which state",
            "how old",
            "बता सकते हैं",
            "कृपया बताएं",
            "आपकी उम्र",
            "कौन से राज्य"
        ]
        
        response_lower = response_text.lower()
        return any(keyword in response_lower for keyword in clarification_keywords)
    
    def _get_fallback_response(self, language: str) -> str:
        """Get fallback response when Gemini fails"""
        fallback_responses = {
            "hi": "क्षमा करें, मुझे आपकी मदद करने में समस्या हो रही है। कृपया अपना सवाल फिर से पूछें या हमारी हेल्पलाइन 1800-XXX-XXXX पर संपर्क करें।",
            "en": "Sorry, I'm having trouble helping you right now. Please try asking your question again or contact our helpline at 1800-XXX-XXXX."
        }
        return fallback_responses.get(language, fallback_responses["en"])
    
    async def translate_text(self, text: str, target_language: str) -> str:
        """Translate text to target language using Gemini"""
        try:
            prompt = f"Translate the following text to {target_language}. Only provide the translation, nothing else:\n\n{text}"
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return text  # Return original if translation fails
    
    async def summarize_scheme(self, scheme_data: Dict[str, Any], language: str) -> str:
        """Generate a concise summary of a scheme in target language"""
        try:
            scheme_json = json.dumps(scheme_data, indent=2, ensure_ascii=False)
            prompt = f"""Summarize this government scheme in {language} language in 2-3 simple sentences suitable for voice output:

{scheme_json}

Provide only the summary, nothing else."""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Summarization error: {str(e)}")
            return scheme_data.get('description', {}).get(language, scheme_data.get('description', {}).get('en', ''))


# Singleton instance
gemini_service = GeminiService()
