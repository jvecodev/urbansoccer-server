# urbansoccer_server/services/tts_provider.py
import requests
import logging
from urbansoccer_server.core.config import settings
from typing import Optional

logger = logging.getLogger(__name__)

# URL para o servidor Flask oficial da Coqui
COQUI_TTS_URL = f"{settings.COQUI_TTS_URL}/api/tts"

async def generate_audio_from_text(text: str) -> Optional[bytes]:
    """
    Usa o serviço Coqui TTS (servidor Flask) para converter texto em áudio.
    """
    # Payload para a API do Flask
    payload = {
        "text": text,
        "language_id": "pt", # Para o xtts_v2, usamos language_id
        "speaker_id": "p225"  # Um exemplo de voz, pode ser trocado
    }
    try:
        # A requisição volta a ser um POST com corpo JSON
        response = requests.post(COQUI_TTS_URL, json=payload)
        response.raise_for_status()
        return response.content  # Retorna os bytes do áudio (WAV)

    except requests.RequestException as e:
        logger.error(f"Erro ao contatar o Coqui TTS (Flask). Erro: {e}")
        return None