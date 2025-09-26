# urbansoccer_server/services/llm_provider.py
import os
import aiohttp
import json
import logging
import google.generativeai as genai  
from urbansoccer_server.core.config import settings

logger = logging.getLogger(__name__)

GOOGLE_AISTUDIO_MODELS = ["gemini-1.5-flash"]
CEREBRAS_MODELS = ["llama3.1-8b", "llama3.1-70b"] 
GROQ_MODELS = ["llama3-70b-8192"]

# Configurar Google GenAI
GOOGLE_CLIENT = None
if settings.GOOGLE_AISTUDIO_KEY:
    try:
        genai.configure(api_key=settings.GOOGLE_AISTUDIO_KEY)
        GOOGLE_CLIENT = True
        logger.info("Cliente Google GenAI configurado com sucesso")
    except Exception as e:
        logger.error(f"Falha ao configurar o cliente Google GenAI: {e}")
        GOOGLE_CLIENT = None
else:
    GOOGLE_CLIENT = None

timeout = aiohttp.ClientTimeout(total=90)



def convert_prompt_to_messages(prompt: str) -> list[dict]:
    return [{"role": "user", "content": prompt}]

async def google_aistudio_request(messages: list[dict]) -> str | None:
    if not GOOGLE_CLIENT:
        logger.warning("Cliente Google GenAI não configurado. Pulando.")
        return None
    try:
        model = genai.GenerativeModel(GOOGLE_AISTUDIO_MODELS[0])
        
        # Converter mensagens para formato do Google
        prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        prompt += "\n\nPor favor, responda apenas com um JSON válido."
        
        response = await model.generate_content_async(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        return response.text.strip()
    except Exception as e:
        logger.error(f"Erro na requisição para Google AI Studio: {e}")
    return None

async def cerebras_request(messages: list[dict]) -> str | None:
    if not settings.CEREBRAS_KEY:
        logger.warning("Chave da API Cerebras não configurada. Pulando.")
        return None
        
    headers = {"Authorization": f"Bearer {settings.CEREBRAS_KEY}", "Content-Type": "application/json"}
    try:
        async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
            for model in CEREBRAS_MODELS:
                try:
                    # Adicionar instrução para resposta em JSON
                    enhanced_messages = messages.copy()
                    enhanced_messages.append({
                        "role": "system", 
                        "content": "Responda apenas com um JSON válido. Não inclua texto adicional."
                    })
                    
                    payload = {"model": model, "messages": enhanced_messages}
                    async with session.post(
                        "https://api.cerebras.ai/v1/chat/completions",
                        json=payload
                    ) as response:
                        response.raise_for_status()
                        json_response = await response.json()
                        if 'error' not in json_response:
                            return json_response["choices"][0]["message"]["content"].strip()
                except Exception as e:
                    logger.error(f"Modelo Cerebras '{model}' falhou: {e}")
                    continue
    except Exception as e:
        logger.error(f"Erro na requisição para Cerebras: {e}")
    return None

async def groq_request(messages: list[dict]) -> str | None:
    if not settings.GROQ_KEY:
        logger.warning("Chave da API Groq não configurada. Pulando.")
        return None

    headers = {"Authorization": f"Bearer {settings.GROQ_KEY}", "Content-Type": "application/json"}
    try:
        async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
            for model in GROQ_MODELS:
                try:
                    # Adicionar instrução para resposta em JSON nas mensagens
                    enhanced_messages = messages.copy()
                    enhanced_messages.append({
                        "role": "system", 
                        "content": "Responda apenas com um JSON válido. Não inclua texto adicional."
                    })
                    
                    payload = {
                        "model": model,
                        "messages": enhanced_messages
                    }
                    async with session.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        json=payload
                    ) as response:
                        response.raise_for_status()
                        json_response = await response.json()
                        if 'error' not in json_response:
                            content = json_response["choices"][0]["message"]["content"]
                            return content.strip()
                except Exception as e:
                    logger.error(f"Modelo Groq '{model}' falhou: {e}")
                    continue
    except Exception as e:
        logger.error(f"Erro na requisição para Groq: {e}")
    return None


async def generate_with_fallback(prompt: str) -> str:
    messages = convert_prompt_to_messages(prompt)
    
    providers = [
        ("GOOGLE AISTUDIO", google_aistudio_request),
        ("CEREBRAS", cerebras_request),
        ("GROQ", groq_request),
    ]
    
    for name, func in providers:
        try:
            logger.info(f"🚀 Tentando provedor de LLM: {name}")
            response = await func(messages)
            if response:
                try:
                    json.loads(response)
                    logger.info(f"✅ SUCESSO com {name}! Resposta válida recebida.")
                    return response
                except json.JSONDecodeError:
                    logger.error(f"❌ Resposta de {name} não é um JSON válido: {response[:200]}...")
                    continue
            else:
                logger.warning(f"⚠️ {name} retornou resposta vazia")
        except Exception as e:
            logger.error(f"💥 Falha ao usar o provedor {name}: {e}")
            
    logger.error("🚫 Todos os provedores de LLM falharam.")
    return '{"error": "Todos os provedores de LLM falharam em gerar uma resposta válida."}'