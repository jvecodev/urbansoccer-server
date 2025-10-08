import random
from typing import Dict, List, Tuple

ALL_CARDS = {
    # Ataque
    "chutar_area": {"actionId": "chutar_area", "label": "Chutar da Área", "description": "Um chute forte e preciso de perto."},
    "chutar_fora": {"actionId": "chutar_fora", "label": "Chutar de Longe", "description": "Tente surpreender com um foguete."},
    "drible_curto": {"actionId": "drible_curto", "label": "Drible Curto", "description": "Passe pelo marcador na habilidade."},
    "cavar_falta": {"actionId": "cavar_falta", "label": "Cavar Falta", "description": "Use a malandragem para conseguir uma bola parada."},
    
    # Meio-campo / Construção
    "drible_rapido": {"actionId": "drible_rapido", "label": "Drible Rápido", "description": "Use sua velocidade para avançar."},
    "passe_longo": {"actionId": "passe_longo", "label": "Lançamento", "description": "Encontre um companheiro livre no ataque."},
    "tocar_curto": {"actionId": "tocar_curto", "label": "Passe Curto", "description": "Mantenha a posse e procure espaços."},
    
    # Defesa
    "roubar_bola": {"actionId": "roubar_bola", "label": "Roubar a Bola", "description": "Tente desarmar o adversário limpamente."},
    "dar_carrinho": {"actionId": "dar_carrinho", "label": "Dar um Carrinho", "description": "Uma ação arriscada para cortar a jogada."},
    "recuar_bola": {"actionId": "recuar_bola", "label": "Recuar a Bola", "description": "Alivie a pressão e reinicie a jogada."}
}

# Define quais cards estão disponíveis em cada contexto
CONTEXT_CARDS = {
    "meio_campo": [ALL_CARDS["drible_rapido"], ALL_CARDS["passe_longo"], ALL_CARDS["tocar_curto"]],
    "ataque": [ALL_CARDS["chutar_area"], ALL_CARDS["drible_curto"], ALL_CARDS["cavar_falta"]],
    "chance_clara_de_gol": [ALL_CARDS["chutar_area"]], # Apenas uma opção: chutar!
    "defesa_pressionada": [ALL_CARDS["roubar_bola"], ALL_CARDS["dar_carrinho"], ALL_CARDS["recuar_bola"]]
}

def get_initial_cards() -> List[Dict]:
    """Retorna as primeiras ações disponíveis no início da partida."""
    return CONTEXT_CARDS["meio_campo"]

#A função agora recebe e retorna o contexto do jogo
def process_player_action(player_stats: Dict, action_id: str, current_context: str) -> Tuple[str, str, List[Dict], bool]:

    """
    Processa a ação, calcula o resultado e retorna os próximos cards e o novo contexto.
    Retorna: (resultado_texto, novo_contexto, proximos_cards, oponente_marcou)
    """
    
    chance_de_sucesso = 50
    opponent_scored = False
    
    #A chance de sucesso pode depender da ação
    if action_id in ["chutar_area", "chutar_fora"]:
        chance_de_sucesso += player_stats.get("attack", 0) // 3
    elif action_id in ["drible_rapido", "drible_curto"]:
        chance_de_sucesso += player_stats.get("speed", 0) // 3
    elif action_id in ["roubar_bola", "dar_carrinho"]:
        chance_de_sucesso += player_stats.get("defense", 0) // 3
    
    sucesso = random.randint(1, 100) < chance_de_sucesso

    if sucesso:
        if current_context == "meio_campo":
            if action_id == "drible_rapido":
                return "Você arranca em velocidade e chega na entrada da área!", "ataque", CONTEXT_CARDS["ataque"], False
            else: 
                return "Com uma bela troca de passes, o time avança!", "ataque", CONTEXT_CARDS["ataque"], False
        
        elif current_context == "ataque":
            if action_id == "chutar_area":
                return "GOL! Que finalização! A bola beija a rede!", "meio_campo", CONTEXT_CARDS["meio_campo"], False
            elif action_id == "drible_curto":
                return "Que drible! Você deixa o zagueiro no chão e fica cara a cara com o goleiro!", "chance_clara_de_gol", CONTEXT_CARDS["chance_clara_de_gol"], False
            else: 
                return "Você sofre a falta perto da área! É uma ótima oportunidade!", "ataque", [ALL_CARDS["chutar_fora"]], False # Cobrança de falta

        elif current_context == "chance_clara_de_gol":
             return "GOLAAAAÇO! Na cara do gol, você não perdoa!", "meio_campo", CONTEXT_CARDS["meio_campo"], False

        elif current_context == "defesa_pressionada":
            return "Com um desarme preciso, você recupera a posse de bola!", "meio_campo", CONTEXT_CARDS["meio_campo"], False

    else: 
        if random.randint(1, 100) < 30: #30% de chance do oponente marcar
            return "Você erra a jogada e o adversário arma um contra-ataque letal. É gol deles.", "meio_campo", CONTEXT_CARDS["meio_campo"], True
        else:
            return "Você perde a bola e agora precisa se defender!", "defesa_pressionada", CONTEXT_CARDS["defesa_pressionada"], False

    return "A jogada segue disputada no meio-campo.", "meio_campo", CONTEXT_CARDS["meio_campo"], False