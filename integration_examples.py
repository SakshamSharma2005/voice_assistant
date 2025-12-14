"""
Integration examples for different platforms
"""

# ==============================================================================
# EXAMPLE 1: React/Next.js Web App Integration
# ==============================================================================

"""
// Install: npm install axios

import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Create API client
const schemeAPI = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Start a session
async function startSession(language = 'hi', userContext = {}) {
  try {
    const response = await schemeAPI.post('/session/start', {
      language,
      user_context: userContext,
    });
    
    return response.data;
  } catch (error) {
    console.error('Failed to start session:', error);
    throw error;
  }
}

// Send a chat query
async function sendQuery(query, language = 'hi', sessionId = null, userContext = {}) {
  try {
    const response = await schemeAPI.post('/chat/query', {
      query,
      language,
      session_id: sessionId,
      user_context: userContext,
      voice_input: false,
    });
    
    return response.data;
  } catch (error) {
    console.error('Query failed:', error);
    throw error;
  }
}

// Check eligibility
async function checkEligibility(userProfile) {
  try {
    const response = await schemeAPI.post('/eligibility/check', {
      user_profile: userProfile,
      include_state_schemes: true,
    });
    
    return response.data;
  } catch (error) {
    console.error('Eligibility check failed:', error);
    throw error;
  }
}

// Text-to-Speech
async function textToSpeech(text, language = 'hi') {
  try {
    const response = await schemeAPI.post('/voice/synthesize', {
      text,
      language,
      voice_gender: 'female',
      speech_rate: 0.9,
    });
    
    // Play audio
    const audio = new Audio(API_BASE_URL + response.data.audio_url);
    audio.play();
    
    return response.data;
  } catch (error) {
    console.error('TTS failed:', error);
    throw error;
  }
}

// Example usage in a React component
function SchemeAssistant() {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState('');
  
  useEffect(() => {
    // Start session on mount
    startSession('hi', { state: 'Uttar Pradesh' }).then(data => {
      setSessionId(data.session_id);
      setMessages([{ role: 'assistant', text: data.greeting_message }]);
      
      // Play greeting audio if available
      if (data.greeting_audio_url) {
        new Audio(API_BASE_URL + data.greeting_audio_url).play();
      }
    });
  }, []);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Add user message
    setMessages(prev => [...prev, { role: 'user', text: query }]);
    
    // Send query
    const response = await sendQuery(query, 'hi', sessionId);
    
    // Add assistant response
    setMessages(prev => [...prev, { 
      role: 'assistant', 
      text: response.data.response_text,
      schemes: response.data.schemes
    }]);
    
    // Play audio response
    if (response.data.response_audio_url) {
      new Audio(API_BASE_URL + response.data.response_audio_url).play();
    }
    
    setQuery('');
  };
  
  return (
    <div className="scheme-assistant">
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            {msg.text}
            {msg.schemes && (
              <div className="schemes-list">
                {msg.schemes.map(scheme => (
                  <div key={scheme.scheme_id} className="scheme-card">
                    <h3>{scheme.name}</h3>
                    <p>{scheme.description}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
      
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="अपना सवाल पूछें..."
        />
        <button type="submit">भेजें</button>
      </form>
    </div>
  );
}

export default SchemeAssistant;
"""

# ==============================================================================
# EXAMPLE 2: React Native Mobile App Integration
# ==============================================================================

"""
// Install: npm install axios react-native-sound

import axios from 'axios';
import Sound from 'react-native-sound';

const API_BASE_URL = 'http://your-api-domain.com/api/v1';

class SchemeNavigatorAPI {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
    });
    this.sessionId = null;
  }
  
  async startSession(language = 'hi') {
    const { data } = await this.client.post('/session/start', { language });
    this.sessionId = data.session_id;
    return data;
  }
  
  async sendQuery(query, language = 'hi') {
    const { data } = await this.client.post('/chat/query', {
      query,
      language,
      session_id: this.sessionId,
      voice_input: false,
    });
    return data;
  }
  
  playAudio(audioUrl) {
    const sound = new Sound(API_BASE_URL + audioUrl, '', (error) => {
      if (error) {
        console.error('Failed to load sound', error);
        return;
      }
      sound.play((success) => {
        if (success) {
          console.log('Audio played successfully');
        }
        sound.release();
      });
    });
  }
}

export default new SchemeNavigatorAPI();
"""

# ==============================================================================
# EXAMPLE 3: Simple HTML/JavaScript Widget
# ==============================================================================

"""
<!DOCTYPE html>
<html lang="hi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>सरकारी योजना सहायक</title>
  <style>
    .scheme-widget {
      max-width: 600px;
      margin: 20px auto;
      border: 1px solid #ddd;
      border-radius: 10px;
      padding: 20px;
      font-family: Arial, sans-serif;
    }
    .messages {
      height: 400px;
      overflow-y: auto;
      border: 1px solid #eee;
      padding: 10px;
      margin-bottom: 10px;
    }
    .message {
      margin: 10px 0;
      padding: 10px;
      border-radius: 5px;
    }
    .message.user {
      background: #e3f2fd;
      text-align: right;
    }
    .message.assistant {
      background: #f5f5f5;
    }
    input {
      width: 80%;
      padding: 10px;
      border: 1px solid #ddd;
      border-radius: 5px;
    }
    button {
      width: 18%;
      padding: 10px;
      background: #4CAF50;
      color: white;
      border: none;
      border-radius: 5px;
      cursor: pointer;
    }
  </style>
</head>
<body>
  <div class="scheme-widget">
    <h2>🇮🇳 सरकारी योजना सहायक</h2>
    <div id="messages" class="messages"></div>
    <div>
      <input type="text" id="queryInput" placeholder="अपना सवाल पूछें...">
      <button onclick="sendQuery()">भेजें</button>
    </div>
  </div>

  <script>
    const API_BASE = 'http://localhost:8000/api/v1';
    let sessionId = null;
    
    async function init() {
      const response = await fetch(`${API_BASE}/session/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language: 'hi' })
      });
      
      const data = await response.json();
      sessionId = data.session_id;
      
      addMessage('assistant', data.greeting_message);
      
      if (data.greeting_audio_url) {
        playAudio(data.greeting_audio_url);
      }
    }
    
    async function sendQuery() {
      const input = document.getElementById('queryInput');
      const query = input.value.trim();
      
      if (!query) return;
      
      addMessage('user', query);
      input.value = '';
      
      const response = await fetch(`${API_BASE}/chat/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          language: 'hi',
          session_id: sessionId
        })
      });
      
      const data = await response.json();
      addMessage('assistant', data.data.response_text);
      
      if (data.data.response_audio_url) {
        playAudio(data.data.response_audio_url);
      }
    }
    
    function addMessage(role, text) {
      const messagesDiv = document.getElementById('messages');
      const messageDiv = document.createElement('div');
      messageDiv.className = `message ${role}`;
      messageDiv.textContent = text;
      messagesDiv.appendChild(messageDiv);
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
    
    function playAudio(url) {
      const audio = new Audio(API_BASE + url);
      audio.play();
    }
    
    // Initialize on page load
    init();
    
    // Handle Enter key
    document.getElementById('queryInput').addEventListener('keypress', (e) => {
      if (e.key === 'Enter') sendQuery();
    });
  </script>
</body>
</html>
"""

# ==============================================================================
# EXAMPLE 4: Python Client
# ==============================================================================

"""
import requests
from typing import Optional, Dict, Any

class SchemeNavigatorClient:
    '''Python client for Government Scheme Navigator API'''
    
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.session_id: Optional[str] = None
    
    def start_session(self, language: str = "hi", user_context: Dict = None) -> Dict:
        '''Start a new conversation session'''
        response = requests.post(
            f"{self.base_url}/session/start",
            json={
                "language": language,
                "user_context": user_context or {}
            }
        )
        response.raise_for_status()
        data = response.json()
        self.session_id = data["session_id"]
        return data
    
    def send_query(self, query: str, language: str = "hi") -> Dict:
        '''Send a chat query'''
        response = requests.post(
            f"{self.base_url}/chat/query",
            json={
                "query": query,
                "language": language,
                "session_id": self.session_id
            }
        )
        response.raise_for_status()
        return response.json()
    
    def check_eligibility(self, user_profile: Dict) -> Dict:
        '''Check scheme eligibility for a user'''
        response = requests.post(
            f"{self.base_url}/eligibility/check",
            json={"user_profile": user_profile}
        )
        response.raise_for_status()
        return response.json()
    
    def search_schemes(self, criteria: Dict) -> Dict:
        '''Search schemes by criteria'''
        response = requests.post(
            f"{self.base_url}/schemes/search",
            json=criteria
        )
        response.raise_for_status()
        return response.json()


# Example usage
if __name__ == "__main__":
    client = SchemeNavigatorClient()
    
    # Start session
    session = client.start_session(
        language="hi",
        user_context={"state": "Uttar Pradesh", "occupation": "farmer"}
    )
    print(f"Session started: {session['session_id']}")
    print(f"Greeting: {session['greeting_message']}")
    
    # Send query
    response = client.send_query("मुझे किसानों के लिए योजना बताओ", language="hi")
    print(f"\\nAssistant: {response['data']['response_text']}")
    
    # Check eligibility
    eligibility = client.check_eligibility({
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
    })
    
    print(f"\\nEligible schemes: {eligibility['eligible_schemes_count']}")
    for result in eligibility['results'][:3]:
        if result['is_eligible']:
            print(f"- {result['scheme_name']} ({result['match_percentage']}% match)")
"""
