import json
from typing import List, Dict
from . import llm_provider, prompt_templates
async def generate_campaign_options(player_info: Dict) -> List[Dict]:
    prompt = prompt_templates.GENERATE_CAMPAIGNS_PROMPT.format(
        player_name=player_info.get("name"),
        player_description=player_info.get("description"),
        player_special_ability=player_info.get("stats", {}).get("specialAbility")
    )

    llm_response_text = await llm_provider.generate_with_fallback(prompt)

    try:
        response_json = json.loads(llm_response_text)
        return response_json.get("campaigns", [])
    except (json.JSONDecodeError, AttributeError):
        return [{"campaignName": "Erro de Geração", "description": "Não foi possível gerar as campanhas."}]