import requests
import json
import logging
from urbansoccer_server.core.config import settings

logger = logging.getLogger(__name__)

async def generate_with_ollama(prompt: str) -> str:
    url = f"{settings.OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": "qwen2.5:0.5b",  
        "prompt": prompt,
        "stream": False,
        "format": "json" 
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        full_response_json = json.loads(response.text)
        return full_response_json.get("response", "")
    except requests.RequestException as e:
        logger.error(f"Erro ao contatar o Ollama. Certifique-se de que ele está rodando com 'ollama serve'. Erro: {e}")
        return '{"error": "Ollama is not running or not reachable."}'
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar a resposta JSON do Ollama: {e}. Resposta recebida: {response.text}")
        return '{"error": "Failed to decode JSON from Ollama."}'