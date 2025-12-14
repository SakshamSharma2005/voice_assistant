"""
Simple API tests
Run with: pytest test_api.py
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_start_session():
    """Test session start"""
    response = client.post(
        "/api/v1/session/start",
        json={"language": "hi"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "greeting_message" in data
    return data["session_id"]


def test_list_schemes():
    """Test listing all schemes"""
    response = client.get("/api/v1/schemes?limit=10")
    assert response.status_code == 200
    schemes = response.json()
    assert isinstance(schemes, list)
    assert len(schemes) > 0


def test_get_scheme_by_id():
    """Test getting specific scheme"""
    response = client.get("/api/v1/schemes/PM-KISAN-001")
    assert response.status_code == 200
    scheme = response.json()
    assert scheme["scheme_id"] == "PM-KISAN-001"
    assert "name" in scheme
    assert "eligibility" in scheme


def test_search_schemes():
    """Test scheme search"""
    response = client.post(
        "/api/v1/schemes/search",
        json={
            "age": 45,
            "occupation": "farmer",
            "state": "Uttar Pradesh"
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert "total" in result
    assert "schemes" in result
    assert result["total"] > 0


def test_check_eligibility():
    """Test eligibility check"""
    response = client.post(
        "/api/v1/eligibility/check",
        json={
            "user_profile": {
                "age": 45,
                "gender": "male",
                "state": "Uttar Pradesh",
                "occupation": "farmer",
                "annual_income": 150000,
                "is_farmer": True,
                "land_size_acres": 2.5,
                "has_aadhaar": True,
                "has_bank_account": True,
                "preferred_language": "hi"
            }
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert "eligible_schemes_count" in result
    assert "results" in result
    assert len(result["results"]) > 0


def test_text_to_speech():
    """Test TTS synthesis"""
    response = client.post(
        "/api/v1/voice/synthesize",
        json={
            "text": "नमस्ते",
            "language": "hi",
            "voice_gender": "female"
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert result["success"] == True
    assert "audio_url" in result


def test_chat_query():
    """Test chat query endpoint"""
    # Start session first
    session_response = client.post(
        "/api/v1/session/start",
        json={"language": "hi"}
    )
    session_id = session_response.json()["session_id"]
    
    # Send query
    response = client.post(
        "/api/v1/chat/query",
        json={
            "query": "Tell me about farmer schemes",
            "language": "en",
            "session_id": session_id
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert result["success"] == True
    assert "data" in result
    assert "response_text" in result["data"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
