from elevenlabs.client import ElevenLabs
from elevenlabs import Voice, VoiceSettings
from urbansoccer_server.core.config import settings
import logging

logger = logging.getLogger(__name__)

client = None
if settings.ELEVENLABS_API_KEY:
    try:
        client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
        logger.info("✅ Cliente da ElevenLabs conectado com sucesso.")
    except Exception as e:
        logger.error(f"❌ Falha ao conectar com a ElevenLabs: {e}")

async def text_to_speech_stream(text: str):
    """
    Converte texto em um stream de áudio usando a API da ElevenLabs.
    """
    if not client:
        raise RuntimeError("API da ElevenLabs não configurada.")
    
    try:
        # Sintaxe correta da API da ElevenLabs para streaming
        audio_stream = client.text_to_speech.stream(
            text=text,
            voice_id='pNInz6obpgDQGcFmaJgB',
            voice_settings=VoiceSettings(
                stability=0.4, 
                similarity_boost=0.75, 
                style=0.0, 
                use_speaker_boost=True
            )
        )
        return audio_stream
    except Exception as e:
        logger.error(f"Erro ao gerar áudio com ElevenLabs: {e}")
        return None