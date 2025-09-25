# urbansoccer_server/services/tts_provider.py
import requests
import logging
from urbansoccer_server.core.config import settings
from typing import Optional

logger = logging.getLogger(__name__)

# Adicione a nova variável de ambiente no seu arquivo config.py e .env
COQUI_TTS_URL = f"{settings.COQUI_TTS_URL}/api/tts"

async def generate_audio_from_text(text: str) -> Optional[bytes]:
    """
    Usa o serviço Coqui TTS para converter texto em áudio.
    """
    # O modelo XTTS v2 é multilíngue e ótimo para português
    payload = {
        "text": text,
        "model_name": "tts_models/multilingual/multi-dataset/xtts_v2",
        "speaker_wav": "",  # Pode usar para clonagem de voz
        "language": "pt"
    }
    try:
        response = requests.post(COQUI_TTS_URL, json=payload)
        response.raise_for_status()
        return response.content  # Retorna os bytes do áudio (WAV)
    except requests.RequestException as e:
        logger.error(f"Erro ao contatar o Coqui TTS. Erro: {e}")
        return None