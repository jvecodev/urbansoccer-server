# urbansoccer_server/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional 

class Settings(BaseSettings):
    MONGO_URI: str
    MONGO_DB: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    OLLAMA_BASE_URL: Optional[str] = None 
    ELEVENLABS_API_KEY: Optional[str] = None
    
    GOOGLE_AISTUDIO_KEY: Optional[str] = None
    CEREBRAS_KEY: Optional[str] = None
    GROQ_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()