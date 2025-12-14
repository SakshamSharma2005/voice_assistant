"""
Complete Voice Interaction Flow Test
Shows how voice input → processing → voice output works
"""
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"

def complete_voice_interaction_demo():
    """
    Simulates a real voice interaction:
    User speaks → API transcribes → AI processes → API responds with voice
    """
    print("\n" + "="*70)
    print("🎙️  COMPLETE VOICE INTERACTION FLOW")
    print("="*70)
    
    print("\n📱 SCENARIO: A farmer calls the voice helpline about PM Kisan scheme")
    print("-" * 70)
    
    # Step 1: Start Session
    print("\n[STEP 1] 🚀 Starting voice session...")
    session_response = requests.post(f"{BASE_URL}/session/start", json={
        "language": "hi",
        "user_context": {
            "age": 35,
            "occupation": "farmer",
            "state": "Punjab"
        }
    })
    
    if session_response.status_code != 200:
        print(f"❌ Failed to start session: {session_response.text}")
        return
    
    session_data = session_response.json()
    session_id = session_data['session_id']
    greeting = session_data.get('greeting', 'नमस्ते!')
    
    print(f"✅ Session started: {session_id}")
    print(f"📝 Greeting text: {greeting[:80]}...")
    
    # Step 2: Generate greeting audio (what user hears when they call)
    print("\n[STEP 2] 🔊 Generating welcome voice message...")
    welcome_audio = requests.post(f"{BASE_URL}/voice/synthesize", json={
        "text": greeting,
        "language": "hi",
        "speech_rate": 0.9
    })
    
    if welcome_audio.status_code == 200:
        audio_data = welcome_audio.json()
        print(f"✅ Welcome audio generated!")
        print(f"🎧 User hears: http://localhost:8000{audio_data['audio_url']}")
    
    # Step 3: User speaks (we'll simulate with text for now)
    print("\n[STEP 3] 🎤 User speaks their query...")
    user_voice_query = "मुझे पीएम किसान योजना के बारे में बताइए"
    print(f"📢 User said: '{user_voice_query}'")
    print("   (In real app, this would be captured via microphone)")
    
    # Simulating transcription (in real app, audio file would be uploaded to /voice/transcribe)
    print("\n[STEP 4] 📝 Transcribing voice to text...")
    print(f"✅ Transcribed: '{user_voice_query}'")
    
    # Step 5: Send to AI for processing
    print("\n[STEP 5] 🤖 AI processing the query...")
    chat_response = requests.post(f"{BASE_URL}/chat/query", json={
        "session_id": session_id,
        "query": user_voice_query,
        "language": "hi",
        "user_context": {
            "age": 35,
            "occupation": "farmer",
            "state": "Punjab",
            "annual_income": 80000,
            "has_bank_account": True
        }
    })
    
    if chat_response.status_code != 200:
        print(f"❌ Chat failed: {chat_response.text}")
        return
    
    chat_data = chat_response.json()
    ai_response = chat_data['response']
    intent = chat_data.get('intent', 'unknown')
    schemes = chat_data.get('relevant_schemes', [])
    
    print(f"✅ AI understood intent: {intent}")
    print(f"📋 Found {len(schemes)} relevant schemes")
    print(f"💬 AI Response: {ai_response[:200]}...")
    
    # Step 6: Convert AI response to voice
    print("\n[STEP 6] 🔊 Converting AI response to voice...")
    response_audio = requests.post(f"{BASE_URL}/voice/synthesize", json={
        "text": ai_response,
        "language": "hi"
    })
    
    if response_audio.status_code == 200:
        audio_data = response_audio.json()
        print(f"✅ Response audio generated!")
        print(f"🎧 User hears: http://localhost:8000{audio_data['audio_url']}")
    
    # Step 7: Show scheme details (if user wants to know more)
    if schemes:
        print("\n[STEP 7] 📄 Scheme details found:")
        for scheme in schemes[:2]:
            print(f"\n   📌 {scheme['name']['hi']}")
            print(f"      ID: {scheme['scheme_id']}")
            print(f"      Benefit: ₹{scheme['benefits'].get('amount', 'varies')}")
    
    print("\n" + "="*70)
    print("✅ COMPLETE VOICE INTERACTION FLOW SUCCESSFUL!")
    print("="*70)
    
    return {
        "session_id": session_id,
        "greeting_audio": audio_data['audio_url'] if welcome_audio.status_code == 200 else None,
        "response_audio": audio_data['audio_url'] if response_audio.status_code == 200 else None
    }

def show_voice_architecture():
    """Show how the voice system works"""
    print("\n" + "="*70)
    print("🏗️  VOICE SYSTEM ARCHITECTURE")
    print("="*70)
    
    architecture = """
    
    [USER SPEAKS] → [MICROPHONE/PHONE] → [YOUR API]
                                              ↓
    ┌─────────────────────────────────────────────────────────────┐
    │  1. VOICE INPUT (Speech-to-Text)                           │
    │     POST /api/v1/voice/transcribe                          │
    │     • Upload audio file (MP3/WAV/WebM)                     │
    │     • Returns: Text transcript + language                  │
    │                                                             │
    │  2. TEXT PROCESSING (AI Understanding)                     │
    │     POST /api/v1/chat/query                                │
    │     • Send transcribed text                                │
    │     • AI understands intent                                │
    │     • Searches relevant schemes                            │
    │     • Generates response                                   │
    │                                                             │
    │  3. VOICE OUTPUT (Text-to-Speech)                          │
    │     POST /api/v1/voice/synthesize                          │
    │     • Convert AI response to audio                         │
    │     • Returns: Audio URL                                   │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘
                                              ↓
    [AUDIO FILE] → [PHONE/SPEAKER] → [USER HEARS]
    
    """
    print(architecture)
    
    print("\n📋 DETAILED FLOW:")
    print("-" * 70)
    
    flow_steps = [
        ("1️⃣", "User calls helpline", "Phone captures voice"),
        ("2️⃣", "Upload to /voice/transcribe", "Audio → Text conversion"),
        ("3️⃣", "Send text to /chat/query", "AI understands & responds"),
        ("4️⃣", "Send response to /voice/synthesize", "Text → Audio conversion"),
        ("5️⃣", "Play audio to user", "User hears response in their language")
    ]
    
    for emoji, step, detail in flow_steps:
        print(f"{emoji} {step:30} → {detail}")

def test_with_audio_file():
    """Test with actual audio file if available"""
    print("\n" + "="*70)
    print("🎤 TESTING WITH REAL AUDIO FILE")
    print("="*70)
    
    # Check for test audio
    test_files = ["test_audio.mp3", "test_audio.wav", "test.mp3"]
    audio_file = None
    
    for file in test_files:
        if Path(file).exists():
            audio_file = file
            break
    
    if not audio_file:
        print("\n⚠️  No test audio file found.")
        print("\n📝 TO TEST WITH REAL VOICE:")
        print("   1. Record yourself saying: 'मुझे किसान योजना चाहिए'")
        print("   2. Save as 'test_audio.mp3' in this folder")
        print("   3. Run this script again")
        print("\n🎯 OR use Swagger UI:")
        print("   1. Go to http://localhost:8000/api/v1/docs")
        print("   2. Find POST /api/v1/voice/transcribe")
        print("   3. Click 'Try it out'")
        print("   4. Upload your audio file")
        print("   5. See the transcription!")
        return
    
    print(f"\n✅ Found audio file: {audio_file}")
    print("🎧 Transcribing...")
    
    with open(audio_file, 'rb') as f:
        files = {'audio_file': (audio_file, f, 'audio/mpeg')}
        params = {'language': 'hi', 'audio_format': 'mp3'}
        
        response = requests.post(
            f"{BASE_URL}/voice/transcribe",
            files=files,
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Transcription successful!")
            print(f"📝 Text: {data['text']}")
            print(f"🌐 Language: {data['language']}")
            
            # Now send to chat
            print("\n💬 Sending to AI for response...")
            chat_resp = requests.post(f"{BASE_URL}/chat/query", json={
                "query": data['text'],
                "language": data['language']
            })
            
            if chat_resp.status_code == 200:
                chat_data = chat_resp.json()
                print(f"🤖 AI Response: {chat_data['response'][:150]}...")
        else:
            print(f"❌ Transcription failed: {response.text}")

def main():
    print("🎙️  VOICE INTERACTION TESTING SUITE")
    print("="*70)
    
    try:
        # Check server
        health = requests.get("http://localhost:8000/health")
        if health.status_code != 200:
            print("❌ Server not running! Start it first:")
            print("   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
            return
        
        print("✅ Server is running!\n")
        
        # Show architecture
        show_voice_architecture()
        
        # Run complete flow demo
        result = complete_voice_interaction_demo()
        
        # Test with real audio if available
        test_with_audio_file()
        
        print("\n" + "="*70)
        print("📚 SUMMARY: HOW VOICE WORKS IN YOUR API")
        print("="*70)
        print("""
Your voice API has 3 main endpoints:

1️⃣  POST /voice/transcribe
   • Input: Audio file (MP3/WAV/WebM)
   • Output: Text transcript
   • Use: Convert user's voice to text

2️⃣  POST /chat/query
   • Input: Text query + session + user context
   • Output: AI response + relevant schemes
   • Use: Understand intent & generate response

3️⃣  POST /voice/synthesize
   • Input: Text + language
   • Output: Audio file URL
   • Use: Convert response to voice

COMPLETE FLOW:
User Voice → transcribe → AI query → synthesize → User Hears

🔗 Test in Swagger UI: http://localhost:8000/api/v1/docs
        """)
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server!")
        print("Start server: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
