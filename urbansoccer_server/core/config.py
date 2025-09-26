# urbansoccer_server/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional # <-- ADICIONE ESTE IMPORT, se não estiver lá

class Settings(BaseSettings):
    MONGO_URI: str
    MONGO_DB: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- LLM Settings ---
    OLLAMA_BASE_URL: str
    
    # --- CORREÇÃO AQUI ---
    # Tornamos a chave opcional para não quebrar a aplicação se ela não for definida.
    # O valor padrão é None.
    ELEVENLABS_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()