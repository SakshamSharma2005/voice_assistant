"""
Voice Command Testing Script
Tests Speech-to-Text and Text-to-Speech functionality
"""
import requests
import json
import base64
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"

def test_text_to_speech():
    """Test Text-to-Speech (TTS) - Convert text to audio"""
    print("\n" + "="*60)
    print("TEST 1: Text-to-Speech (TTS)")
    print("="*60)
    
    # Test in multiple languages
    test_cases = [
        {
            "text": "Hello, I want to know about farmer schemes",
            "language": "en",
            "name": "English"
        },
        {
            "text": "नमस्ते, मुझे किसान योजनाओं के बारे में जानना है",
            "language": "hi",
            "name": "Hindi"
        },
        {
            "text": "வணக்கம், எனக்கு விவசாய திட்டங்கள் பற்றி தெரிந்து கொள்ள வேண்டும்",
            "language": "ta",
            "name": "Tamil"
        }
    ]
    
    for test in test_cases:
        print(f"\n🎤 Testing {test['name']} TTS...")
        print(f"   Text: {test['text'][:50]}...")
        
        payload = {
            "text": test["text"],
            "language": test["language"],
            "speech_rate": 0.9
        }
        
        try:
            response = requests.post(f"{BASE_URL}/voice/synthesize", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success!")
                print(f"   Audio URL: {data['audio_url']}")
                print(f"   File: {data['filename']}")
                print(f"   Duration: {data.get('duration', 'N/A')}s")
                print(f"   📥 Download: http://localhost:8000{data['audio_url']}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_speech_to_text_with_sample():
    """Test Speech-to-Text (STT) - You need to provide an audio file"""
    print("\n" + "="*60)
    print("TEST 2: Speech-to-Text (STT)")
    print("="*60)
    
    # Check if test audio file exists
    test_audio = Path("test_audio.mp3")
    
    if not test_audio.exists():
        print("\n⚠️  No test audio file found.")
        print("   To test STT, create an audio file named 'test_audio.mp3'")
        print("   Or record yourself saying: 'I am a farmer from Punjab'")
        print("\n   Alternative: Generate audio first using TTS test above")
        return
    
    print(f"\n🎧 Testing with audio file: {test_audio}")
    
    # Upload and transcribe
    with open(test_audio, 'rb') as f:
        files = {'audio_file': ('test_audio.mp3', f, 'audio/mpeg')}
        params = {
            'language': 'en',
            'audio_format': 'mp3'
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/voice/transcribe",
                files=files,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Transcription successful!")
                print(f"   Text: {data['text']}")
                print(f"   Language: {data['language']}")
                print(f"   Confidence: {data.get('confidence', 'N/A')}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_voice_conversation_flow():
    """Test complete voice-based conversation flow"""
    print("\n" + "="*60)
    print("TEST 3: Complete Voice Conversation Flow")
    print("="*60)
    
    # Step 1: Start a session
    print("\n📝 Step 1: Starting conversation session...")
    session_payload = {
        "language": "hi",
        "user_context": {
            "age": 35,
            "occupation": "farmer",
            "state": "Punjab"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/session/start", json=session_payload)
        if response.status_code == 200:
            session_data = response.json()
            session_id = session_data['session_id']
            print(f"   ✅ Session created: {session_id}")
            print(f"   Greeting (Hindi): {session_data['greeting'][:80]}...")
            
            # Generate audio for greeting
            print("\n🔊 Generating audio for greeting...")
            tts_payload = {
                "text": session_data['greeting'],
                "language": "hi"
            }
            tts_response = requests.post(f"{BASE_URL}/voice/synthesize", json=tts_payload)
            if tts_response.status_code == 200:
                tts_data = tts_response.json()
                print(f"   ✅ Audio generated: http://localhost:8000{tts_data['audio_url']}")
            
            # Step 2: User query (simulated voice input as text)
            print("\n💬 Step 2: Processing user query...")
            query = "मुझे किसान योजनाओं के बारे में बताओ"
            print(f"   User (voice→text): {query}")
            
            chat_payload = {
                "session_id": session_id,
                "query": query,
                "language": "hi",
                "user_context": {
                    "age": 35,
                    "occupation": "farmer",
                    "state": "Punjab",
                    "annual_income": 80000
                }
            }
            
            chat_response = requests.post(f"{BASE_URL}/chat/query", json=chat_payload)
            if chat_response.status_code == 200:
                chat_data = chat_response.json()
                print(f"   ✅ AI Response received")
                print(f"   Response: {chat_data['response'][:150]}...")
                print(f"   Intent: {chat_data.get('intent', 'N/A')}")
                print(f"   Schemes found: {len(chat_data.get('relevant_schemes', []))}")
                
                # Generate audio response
                if chat_data.get('audio_url'):
                    print(f"   🔊 Audio response: http://localhost:8000{chat_data['audio_url']}")
                
                # Show scheme recommendations
                if chat_data.get('relevant_schemes'):
                    print(f"\n   📋 Recommended schemes:")
                    for scheme in chat_data['relevant_schemes'][:3]:
                        print(f"      - {scheme['name']['hi']}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_multilingual_voice():
    """Test voice synthesis in multiple Indian languages"""
    print("\n" + "="*60)
    print("TEST 4: Multilingual Voice Support")
    print("="*60)
    
    languages = [
        ("en", "English", "Welcome to Government Scheme Navigator"),
        ("hi", "Hindi", "सरकारी योजना नेविगेटर में आपका स्वागत है"),
        ("ta", "Tamil", "அரசு திட்ட வழிகாட்டிக்கு வரவேற்கிறோம்"),
        ("te", "Telugu", "ప్రభుత్వ పథకం నావిగేటర్‌కు స్వాగతం"),
        ("bn", "Bengali", "সরকারী স্কিম নেভিগেটরে স্বাগতম"),
        ("mr", "Marathi", "सरकारी योजना नेव्हिगेटरमध्ये आपले स्वागत आहे"),
    ]
    
    print("\n🌍 Testing voice generation in 6 languages...\n")
    
    for lang_code, lang_name, text in languages:
        print(f"🎤 {lang_name} ({lang_code}):")
        print(f"   Text: {text}")
        
        payload = {
            "text": text,
            "language": lang_code
        }
        
        try:
            response = requests.post(f"{BASE_URL}/voice/synthesize", json=payload)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Audio: http://localhost:8000{data['audio_url']}\n")
            else:
                print(f"   ❌ Failed: {response.status_code}\n")
        except Exception as e:
            print(f"   ❌ Error: {e}\n")

def demo_voice_use_cases():
    """Show practical use cases for voice features"""
    print("\n" + "="*60)
    print("PRACTICAL VOICE USE CASES")
    print("="*60)
    
    use_cases = [
        {
            "title": "Farmer Query (Hindi)",
            "scenario": "Rural farmer asking about PM Kisan scheme",
            "voice_input": "मुझे पीएम किसान योजना के बारे में बताइए",
            "language": "hi"
        },
        {
            "title": "Pension Inquiry (English)",
            "scenario": "Senior citizen asking about pension schemes",
            "voice_input": "What pension schemes are available for senior citizens?",
            "language": "en"
        },
        {
            "title": "Women Scheme (Tamil)",
            "scenario": "Woman asking about schemes for women",
            "voice_input": "பெண்களுக்கான அரசு திட்டங்கள் என்னென்ன?",
            "language": "ta"
        }
    ]
    
    for idx, case in enumerate(use_cases, 1):
        print(f"\n📱 Use Case {idx}: {case['title']}")
        print(f"   Scenario: {case['scenario']}")
        print(f"   Voice Input: {case['voice_input']}")
        
        # Generate audio for this query
        payload = {
            "text": case['voice_input'],
            "language": case['language']
        }
        
        try:
            response = requests.post(f"{BASE_URL}/voice/synthesize", json=payload)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Sample audio: http://localhost:8000{data['audio_url']}")
        except:
            print(f"   ⚠️  Could not generate sample audio")

def main():
    print("🎙️  VOICE COMMAND TESTING SUITE")
    print("="*60)
    print("Testing Voice-Assisted Government Scheme Navigator API")
    print("Server: http://localhost:8000")
    print("="*60)
    
    try:
        # Check if server is running
        health = requests.get("http://localhost:8000/health")
        if health.status_code != 200:
            print("\n❌ Server not responding! Start server first:")
            print("   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
            return
        
        print("\n✅ Server is running!")
        
        # Run tests
        test_text_to_speech()
        test_multilingual_voice()
        test_voice_conversation_flow()
        demo_voice_use_cases()
        test_speech_to_text_with_sample()
        
        print("\n" + "="*60)
        print("✅ VOICE TESTING COMPLETED!")
        print("="*60)
        print("\n📝 Notes:")
        print("   • All generated audio files are in: storage/audio/")
        print("   • Audio files expire after 24 hours")
        print("   • Click on audio URLs to download and play")
        print("   • For STT testing, record audio with your query")
        print("\n🎯 Next Steps:")
        print("   1. Open audio URLs in browser to hear the voice")
        print("   2. Test with real microphone input")
        print("   3. Try different languages and queries")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to server!")
        print("   Start the server first:")
        print("   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
