# urbansoccer_server/services/game_logic.py
import random
from typing import Dict, List, Tuple


ALL_CARDS = {
    "chutar_area": {"actionId": "chutar_area", "label": "Chutar da Área", "description": "Um chute forte e arriscado de perto."},
    "chutar_fora": {"actionId": "chutar_fora", "label": "Chutar de Longe", "description": "Tente surpreender o goleiro com um foguete."},
    "drible_rapido": {"actionId": "drible_rapido", "label": "Drible Rápido", "description": "Use sua velocidade para passar pelo marcador."},
    "passe_longo": {"actionId": "passe_longo", "label": "Lançamento Longo", "description": "Encontre um companheiro livre no ataque."},
    "tocar_curto": {"actionId": "tocar_curto", "label": "Passe Curto", "description": "Mantenha a posse de bola e procure espaços."}
}

def get_initial_cards() -> List[Dict]:
    """Retorna as primeiras ações disponíveis no início da partida."""
    return [ALL_CARDS["tocar_curto"], ALL_CARDS["drible_rapido"], ALL_CARDS["chutar_fora"]]

def process_player_action(player_stats: Dict, action_id: str) -> Tuple[str, List[Dict]]:
    """
    Processa a ação do jogador, calcula o resultado e retorna os próximos cards.
    Retorna: (string com o resultado, lista de próximos cards)
    """
    outcome = "neutro"
    # Lógica super simples baseada em stats. Isso pode ficar muito mais complexo!
    # Sucesso é mais provável se o stat principal da ação for alto.
    chance_de_sucesso = 50  # Chance base

    if action_id == "chutar_area" or action_id == "chutar_fora":
        chance_de_sucesso += player_stats.get("attack", 0) // 4
    elif action_id == "drible_rapido":
        chance_de_sucesso += player_stats.get("speed", 0) // 4
    elif action_id == "passe_longo":
        chance_de_sucesso += player_stats.get("leadership", 0) // 4
    
    if random.randint(1, 100) < chance_de_sucesso:
        outcome = "sucesso"
    else:
        outcome = "falha"

    # Determina o resultado textual e os próximos cards
    if outcome == "sucesso":
        if "chutar" in action_id:
            return "GOL! A bola está no fundo da rede!", [ALL_CARDS["tocar_curto"]] # Reinicia o jogo
        else:
            return "Você avança com sucesso!", [ALL_CARDS["chutar_area"], ALL_CARDS["tocar_curto"]]
    else: # Falha
        if "chutar" in action_id:
            return "O goleiro faz uma defesa incrível!", [ALL_CARDS["drible_rapido"], ALL_CARDS["passe_longo"]]
        else:
            return "Você perde a posse de bola.", [ALL_CARDS["drible_rapido"], ALL_CARDS["tocar_curto"]]