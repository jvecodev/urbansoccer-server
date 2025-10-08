from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from urbansoccer_server.services import game_logic, game_narrator
from urbansoccer_server.schemas.campaign_schema import GameActionPayload, PlayResponse

from urbansoccer_server.models import campaign_model, player_model, user_character_model
from urbansoccer_server.schemas.campaign_schema import (
    CampaignCreate, 
    CampaignPublic, 
    CampaignList, 
    CampaignUpdate,
    CampaignProgress,
    CampaignWithDetails
)
from urbansoccer_server.core.auth import get_current_user

from urbansoccer_server.services import campaign_generator

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


class CampaignGenerationRequest(BaseModel):

    """Schema para a requisição de geração de campanhas."""
    user_character_id: str

@router.post("/generate-options", status_code=status.HTTP_200_OK)
async def get_campaign_options(
    request: CampaignGenerationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Gera 4 opções de campanhas via IA baseado no personagem.

    Args:
        request: Contém o ID do personagem do usuário.
        current_user: Usuário autenticado.

    Returns:
        Um dicionário com uma lista de opções de campanha.
    """
    user_id = current_user["_id"]
    
    user_char_with_player = await user_character_model.get_user_character_with_player(request.user_character_id, user_id)

    if not user_char_with_player or "player" not in user_char_with_player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personagem do usuário não encontrado."
        )

    player_details = user_char_with_player["player"]
    options = await campaign_generator.generate_campaign_options(player_details)

    return {"options": options}



@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CampaignPublic)
async def create_new_campaign(
    campaign: CampaignCreate, 
    current_user: dict = Depends(get_current_user)
):
    """Cria uma nova campanha para o usuário autenticado.

    Args:
        campaign: Dados da campanha a ser criada.
        current_user: Usuário autenticado.
    Returns:
        A campanha recém-criada.
    """
    user_id = current_user["_id"]
    
    character = await user_character_model.get_user_character_by_id(campaign.userCharacterId, user_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personagem do usuário não encontrado."
        )

    campaign_dict = campaign.model_dump()
    created_campaign = await campaign_model.create_campaign(user_id, campaign_dict)
    return created_campaign


@router.get("/", status_code=status.HTTP_200_OK, response_model=CampaignList)
async def get_user_campaigns(current_user: dict = Depends(get_current_user)):

    """Retorna todas as campanhas do usuário autenticado."""
    campaigns = await campaign_model.get_campaigns_by_user(current_user["_id"])
    return {"campaigns": campaigns}

@router.get("/active", status_code=status.HTTP_200_OK, response_model=CampaignList)
async def get_active_campaigns(current_user: dict = Depends(get_current_user)):

    """Retorna as campanhas ativas do usuário autenticado."""
    campaigns = await campaign_model.get_active_campaigns_by_user(current_user["_id"])
    return {"campaigns": campaigns}

@router.get("/{campaign_id}", status_code=status.HTTP_200_OK, response_model=CampaignPublic)
async def get_campaign(
    campaign_id: str, 
    current_user: dict = Depends(get_current_user)
):
    """Retorna uma campanha específica do usuário."""
    campaign = await campaign_model.get_campaign_by_user_and_id(current_user["_id"], campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campanha não encontrada"
        )
    return campaign

@router.get("/{campaign_id}/details", status_code=status.HTTP_200_OK, response_model=CampaignWithDetails)
async def get_campaign_with_details(
    campaign_id: str, 
    current_user: dict = Depends(get_current_user)
):
    """Retorna campanha com detalhes do usuário e personagem."""
    campaign = await campaign_model.get_campaign_with_details(campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campanha não encontrada"
        )
    
    if campaign["userId"] != current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado à esta campanha"
        )
    
    return campaign


@router.patch("/{campaign_id}/progress", status_code=status.HTTP_200_OK, response_model=CampaignPublic)
async def update_campaign_progress(
    campaign_id: str, 
    progress: CampaignProgress, 
    current_user: dict = Depends(get_current_user)
):
    """Atualiza o progresso da campanha do usuário."""
    existing_campaign = await campaign_model.get_campaign_by_user_and_id(
        current_user["_id"], campaign_id
    )
    if not existing_campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campanha não encontrada"
        )
    
    progress_dict = progress.model_dump()
    updated_campaign = await campaign_model.update_campaign_progress(campaign_id, progress_dict)
    return updated_campaign

@router.patch("/{campaign_id}/abandon", status_code=status.HTTP_200_OK, response_model=CampaignPublic)
async def abandon_campaign(
    campaign_id: str, 
    current_user: dict = Depends(get_current_user)
):
    """Marca uma campanha ativa como 'abandonada'."""
    existing_campaign = await campaign_model.get_campaign_by_user_and_id(
        current_user["_id"], campaign_id
    )
    if not existing_campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campanha não encontrada"
        )
    
    if existing_campaign["status"] != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas campanhas ativas podem ser abandonadas"
        )
    
    updated_campaign = await campaign_model.abandon_campaign(campaign_id)
    return updated_campaign

@router.patch("/{campaign_id}/complete", status_code=status.HTTP_200_OK, response_model=CampaignPublic)
async def complete_campaign(
    campaign_id: str, 
    current_user: dict = Depends(get_current_user)
):
    """Marca uma campanha ativa como 'completada'."""
    existing_campaign = await campaign_model.get_campaign_by_user_and_id(
        current_user["_id"], campaign_id
    )
    if not existing_campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campanha não encontrada"
        )
    
    if existing_campaign["status"] != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas campanhas ativas podem ser completadas"
        )
    
    updated_campaign = await campaign_model.complete_campaign(campaign_id)
    return updated_campaign

@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: str, 
    current_user: dict = Depends(get_current_user)
):
    """Deleta uma campanha permanentemente."""
    existing_campaign = await campaign_model.get_campaign_by_user_and_id(
        current_user["_id"], campaign_id
    )
    if not existing_campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campanha não encontrada"
        )
    
    success = await campaign_model.delete_campaign(campaign_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao deletar campanha"
        )

@router.get("/{campaign_id}/start", status_code=status.HTTP_200_OK, response_model=PlayResponse)
async def start_game(
    campaign_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Inicia uma partida, retornando narração e ações iniciais."""
    user_id = current_user["_id"]
    campaign = await campaign_model.get_campaign_by_user_and_id(user_id, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campanha não encontrada.")

    initial_narration = campaign.get("description", "A jornada começa agora.")

    initial_cards = game_logic.get_initial_cards()

    initial_game_state = {
        "score": "0 - 0",
        "time": 0,
        "commentary": "A bola vai rolar!",
        "gameContext": "meio_campo"
    }

    return {
        "narration": initial_narration,
        "availableCards": initial_cards,
        "gameState": initial_game_state
    }


@router.post("/{campaign_id}/play", status_code=status.HTTP_200_OK, response_model=PlayResponse)
async def play_turn(
    campaign_id: str,
    payload: GameActionPayload,
    current_user: dict = Depends(get_current_user)
):
    """Processa uma ação do jogador e retorna o novo estado do jogo."""
    user_id = current_user["_id"]
    
    campaign = await campaign_model.get_campaign_by_user_and_id(user_id, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campanha não encontrada.")
    
    character = await user_character_model.get_user_character_with_player(campaign["userCharacterId"], user_id)
    if not character or "player" not in character:
        raise HTTPException(status_code=404, detail="Personagem associado não encontrado.")

    player_stats = character["player"]["stats"]
    player_name = character["characterName"]

    progress = CampaignProgress(**campaign.get("progress", {}))
    current_game_context = progress.gameContext

    outcome_text, new_game_context, next_cards, opponent_scored = game_logic.process_player_action(
        player_stats, payload.actionId, current_game_context
    )
    
    if "GOL!" in outcome_text:
        progress.score += 1
    
    if opponent_scored:
        progress.opponent_score += 1
        
    progress.time += 1
    progress.availableCards = next_cards
    progress.gameContext = new_game_context 
    
    game_over = False
    final_narration = ""
    
    if progress.score >= 3:
        await campaign_model.complete_campaign(campaign_id)
        game_over = True
        final_narration = f"VITÓRIA! Com {progress.score} gols, você é a lenda das ruas! Placar final: {progress.score} a {progress.opponent_score}."
        next_cards = []
    elif progress.opponent_score >= 3:
        await campaign_model.abandon_campaign(campaign_id) 
        game_over = True
        final_narration = f"FIM DE JOGO! O adversário foi melhor hoje. Placar final: {progress.score} a {progress.opponent_score}."
        next_cards = []
    elif progress.time >= 10:
        await campaign_model.complete_campaign(campaign_id) if progress.score >= progress.opponent_score else await campaign_model.abandon_campaign(campaign_id)
        game_over = True
        if progress.score > progress.opponent_score:
             final_narration = f"FIM DE JOGO! Você venceu por {progress.score} a {progress.opponent_score}!"
        elif progress.score < progress.opponent_score:
            final_narration = f"FIM DE JOGO! Você foi derrotado por {progress.score} a {progress.opponent_score}."
        else:
            final_narration = f"EMPATE! O jogo termina com o placar de {progress.score} a {progress.opponent_score}."
        next_cards = []

    await campaign_model.update_campaign_progress(campaign_id, progress.model_dump())

    if game_over:
        return {
            "narration": final_narration,
            "availableCards": [],
            "gameState": {
                "score": f"Jogador {progress.score} - {progress.opponent_score} Adversário",
                "time": progress.time,
                "commentary": "Partida Finalizada!",
                "gameContext": "fim_de_jogo"
            }
        }
    
    previous_outcome_text = campaign.get("progress", {}).get("commentary", "O jogo começa.")
    
    narration_event = {
        "game_context": new_game_context,
        "previous_outcome": previous_outcome_text,
        "player_name": player_name,
        "action_description": f"ação {payload.actionId}",
        "outcome": outcome_text,
        "score": f"Jogador {progress.score} - {progress.opponent_score} Adversário"
    }
    narration_text = await game_narrator.narrate_event(narration_event)

    return {
        "narration": narration_text,
        "availableCards": next_cards,
        "gameState": {
            "score": f"Jogador {progress.score} - {progress.opponent_score} Adversário",
            "time": progress.time,
            "commentary": outcome_text,
            "gameContext": new_game_context
        }
    }

@router.post("/{campaign_id}/reset", status_code=status.HTTP_200_OK, response_model=CampaignPublic)
async def reset_campaign_progress(
    campaign_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Reseta o progresso de uma campanha para o estado inicial."""
    existing_campaign = await campaign_model.get_campaign_by_user_and_id(
        current_user["_id"], campaign_id
    )
    if not existing_campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campanha não encontrada"
        )

    updated_campaign = await campaign_model.reset_campaign(campaign_id)

    if not updated_campaign:
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Não foi possível resetar a campanha."
        )

    return updated_campaign

@router.get("/{campaign_id}/resume", status_code=status.HTTP_200_OK, response_model=PlayResponse)
async def resume_game(
    campaign_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Retoma uma partida, retornando o último estado salvo."""
    user_id = current_user["_id"]
    campaign = await campaign_model.get_campaign_by_user_and_id(user_id, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campanha não encontrada.")

    if campaign["status"] != "active":
        raise HTTPException(status_code=400, detail="Esta campanha não está ativa.")
        
    progress = CampaignProgress(**campaign.get("progress", {}))

    game_state = {
        "score": f"Jogador {progress.score} - {progress.opponent_score} Adversário",
        "time": progress.time,
        "commentary": "A partida continua!",
        "gameContext": progress.gameContext
    }

    return {
        "narration": "Bem-vindo de volta! O jogo continua de onde você parou.",
        "availableCards": progress.availableCards,
        "gameState": game_state
    }