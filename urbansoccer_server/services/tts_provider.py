import requests
import logging
from urbansoccer_server.core.config import settings
from typing import Optional

logger = logging.getLogger(__name__)

COQUI_TTS_URL = f"{settings.COQUI_TTS_URL}/api/tts"

async def generate_audio_from_text(text: str) -> Optional[bytes]:
    payload = {
        "text": text,
        "language_id": "pt",
        # Use uma das vozes que você descobrir com o comando de teste
        "speaker_id": "Ana Florence" 
    }
    try:
        response = requests.post(COQUI_TTS_URL, json=payload)
        response.raise_for_status()
        return response.content

    except requests.RequestException as e:
        logger.error(f"Erro ao contatar o Coqui TTS. Erro: {e}")
        return None