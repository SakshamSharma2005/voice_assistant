from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # API Configuration
    API_VERSION: str = "v1"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    PROJECT_NAME: str = "Government Scheme Navigator API"
    
    # Google Gemini API
    GEMINI_API_KEY: str = Field(default="")
    GEMINI_MODEL: str = "gemini-pro"
    
    # Google Cloud Credentials
    GOOGLE_APPLICATION_CREDENTIALS: str = ""
    GCP_PROJECT_ID: str = ""
    
    # Database Configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "scheme_navigator"
    POSTGRES_URL: str = ""
    
    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    
    # Session Configuration
    SESSION_EXPIRE_MINUTES: int = 30
    MAX_SESSIONS_PER_USER: int = 5
    
    # API Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Audio Configuration
    MAX_AUDIO_FILE_SIZE_MB: int = 10
    SUPPORTED_AUDIO_FORMATS: str = "wav,mp3,webm,ogg"
    AUDIO_OUTPUT_FORMAT: str = "mp3"
    TTS_SPEECH_RATE: float = 1.0
    TTS_PITCH: float = 0.0
    
    # Storage Configuration
    AUDIO_STORAGE_PATH: str = "./storage/audio"
    TEMP_AUDIO_PATH: str = "./storage/temp"
    AUDIO_RETENTION_HOURS: int = 24
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    # Supported Languages
    SUPPORTED_LANGUAGES: List[str] = ["en", "hi", "ta", "te", "bn", "mr", "gu", "kn", "ml", "pa", "or"]
    DEFAULT_LANGUAGE: str = "hi"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def supported_audio_formats_list(self) -> List[str]:
        return [fmt.strip() for fmt in self.SUPPORTED_AUDIO_FORMATS.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


# Initialize settings
settings = Settings()

# Create necessary directories
os.makedirs(settings.AUDIO_STORAGE_PATH, exist_ok=True)
os.makedirs(settings.TEMP_AUDIO_PATH, exist_ok=True)
os.makedirs("./logs", exist_ok=True)
