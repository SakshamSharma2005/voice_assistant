# Voice-Assisted Government Scheme Navigator API

A comprehensive REST API for helping underserved citizens navigate government schemes in India through voice and multilingual support.

## Features

- 🎤 **Voice-First**: Speech-to-text and text-to-speech capabilities
- 🌍 **Multilingual**: Support for 11+ Indian languages
- 🤖 **AI-Powered**: Google Gemini integration for intelligent conversations
- 📱 **Low-Bandwidth Friendly**: Optimized for poor connectivity areas
- 🔒 **Secure**: Session-based authentication and data encryption
- 🐳 **Docker Ready**: Easy deployment with Docker Compose

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (optional)
- Google Gemini API key
- Google Cloud credentials (for Speech APIs)

### Installation

1. **Clone and navigate to project**
```powershell
cd f:\haribhaivoiceasssitant
```

2. **Create virtual environment**
```powershell
python -m venv venv
.\venv\Scripts\Activate
```

3. **Install dependencies**
```powershell
pip install -r requirements.txt
```

4. **Configure environment**
```powershell
cp .env.example .env
# Edit .env with your API keys
```

5. **Run with Docker Compose (Recommended)**
```powershell
docker-compose up -d
```

OR **Run directly**
```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Access API Documentation**
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## API Endpoints

### Voice Processing
- `POST /api/v1/voice/transcribe` - Convert speech to text
- `POST /api/v1/voice/synthesize` - Convert text to speech

### Chat & Query
- `POST /api/v1/chat/query` - Send queries and get AI responses

### Schemes
- `POST /api/v1/schemes/search` - Search schemes by criteria
- `GET /api/v1/schemes/{scheme_id}` - Get scheme details

### Eligibility
- `POST /api/v1/eligibility/check` - Check scheme eligibility

### Session
- `POST /api/v1/session/start` - Start conversation session

## Project Structure

```
f:\haribhaivoiceasssitant/
├── app/
│   ├── api/
│   │   ├── routes/          # API endpoints
│   │   └── dependencies.py   # Shared dependencies
│   ├── services/            # Business logic
│   ├── models/              # Data models
│   ├── data/                # Schemes database
│   ├── utils/               # Utilities
│   ├── config.py            # Configuration
│   └── main.py              # Application entry
├── storage/                 # Audio files storage
├── logs/                    # Application logs
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Technology Stack

- **Backend**: FastAPI (Python 3.11)
- **AI/LLM**: Google Gemini API
- **Speech**: Google Cloud Speech-to-Text & Text-to-Speech
- **Database**: MongoDB
- **Cache**: Redis
- **Deployment**: Docker

## Development

### Running Tests
```powershell
pytest
```

### Code Formatting
```powershell
black app/
```

## License

MIT License - Built for Digital & Inclusive Governance Hackathon

## Support

For issues and questions, please create an issue in the repository.
