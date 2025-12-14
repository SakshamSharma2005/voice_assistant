"""Quick API Test Script"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    """Test health endpoint"""
    print("\n1. Testing Health Endpoint...")
    response = requests.get("http://localhost:8000/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

def test_list_schemes():
    """Test listing all schemes"""
    print("\n2. Testing List All Schemes...")
    response = requests.get(f"{BASE_URL}/schemes/")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Total Schemes: {data['total']}")
    print(f"   First 3 Schemes:")
    for scheme in data['schemes'][:3]:
        print(f"      - {scheme['scheme_id']}: {scheme['name']['en']}")

def test_get_scheme():
    """Test getting a specific scheme"""
    print("\n3. Testing Get Specific Scheme (PM-KISAN)...")
    response = requests.get(f"{BASE_URL}/schemes/PM-KISAN-001")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Scheme: {data['name']['en']}")
    print(f"   Ministry: {data['ministry']}")
    print(f"   Benefit: ₹{data['benefits']['amount']} {data['benefits']['frequency']}")

def test_search_schemes():
    """Test searching schemes"""
    print("\n4. Testing Search Schemes (farmers)...")
    payload = {
        "occupation": ["farmer"],
        "state": "all"
    }
    response = requests.post(f"{BASE_URL}/schemes/search", json=payload)
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Found {len(data['schemes'])} schemes for farmers")
    for scheme in data['schemes'][:3]:
        print(f"      - {scheme['scheme']['name']['en']} (Score: {scheme['match_score']:.1f})")

def test_eligibility():
    """Test eligibility check"""
    print("\n5. Testing Eligibility Check...")
    payload = {
        "user_profile": {
            "age": 35,
            "gender": "male",
            "state": "Punjab",
            "occupation": "farmer",
            "annual_income": 80000,
            "has_bank_account": True,
            "has_aadhaar": True,
            "marital_status": "married"
        }
    }
    response = requests.post(f"{BASE_URL}/eligibility/quick-check", json=payload)
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Eligible for {len(data['eligible_schemes'])} schemes:")
    for result in data['eligible_schemes'][:3]:
        print(f"      - {result['scheme_name']['en']}")
        print(f"        Match: {result['match_percentage']:.1f}%, Priority: {result['priority']}")

def test_session():
    """Test session management"""
    print("\n6. Testing Session Management...")
    payload = {
        "language": "hi"
    }
    response = requests.post(f"{BASE_URL}/session/start", json=payload)
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Session ID: {data['session_id']}")
    print(f"   Greeting (Hindi): {data['greeting'][:80]}...")
    return data['session_id']

def test_chat(session_id):
    """Test chat query"""
    print("\n7. Testing Chat Query...")
    payload = {
        "session_id": session_id,
        "query": "I am a farmer looking for financial help",
        "language": "en",
        "user_context": {
            "age": 35,
            "occupation": "farmer",
            "state": "Punjab"
        }
    }
    response = requests.post(f"{BASE_URL}/chat/query", json=payload)
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Response: {data['response'][:200]}...")
    print(f"   Intent: {data.get('intent', 'N/A')}")
    print(f"   Schemes Mentioned: {len(data.get('relevant_schemes', []))}")

def test_speech_synthesis():
    """Test text-to-speech"""
    print("\n8. Testing Speech Synthesis...")
    payload = {
        "text": "नमस्ते, मैं आपकी सहायता के लिए यहाँ हूँ",
        "language": "hi"
    }
    response = requests.post(f"{BASE_URL}/voice/synthesize", json=payload)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Audio URL: {data['audio_url']}")
        print(f"   Duration: {data.get('duration', 'N/A')}s")
    else:
        print(f"   Error: {response.text}")

if __name__ == "__main__":
    print("=" * 60)
    print("Voice-Assisted Government Scheme Navigator API - Quick Test")
    print("=" * 60)
    
    try:
        test_health()
        test_list_schemes()
        test_get_scheme()
        test_search_schemes()
        test_eligibility()
        session_id = test_session()
        test_chat(session_id)
        test_speech_synthesis()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
