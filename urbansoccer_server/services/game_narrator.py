# urbansoccer_server/services/game_narrator.py
import json
from typing import Dict
from . import llm_provider, prompt_templates

async def narrate_event(event_data: Dict) -> str:

    """
    Usa o LLM para gerar a narração de um evento do jogo.
    """
    
    prompt = prompt_templates.NARRATE_GAME_EVENT_PROMPT.format(
        game_context=event_data.get("game_context", "partida equilibrada"),
        previous_outcome=event_data.get("previous_outcome", "o jogo começou"),
        player_name=event_data.get("player_name", "o jogador"),
        action_description=event_data.get("action_description", "uma ação incrível"),
        outcome=event_data.get("outcome", "algo aconteceu"),
        score=event_data.get("score", "o placar está indefinido")
    )

    llm_response_text = await llm_provider.generate_with_fallback(prompt)

    try:
        response_json = json.loads(llm_response_text)
        return response_json.get("narration", "Jogada continua...")
    except (json.JSONDecodeError, AttributeError):
        return "Juiz apita!"