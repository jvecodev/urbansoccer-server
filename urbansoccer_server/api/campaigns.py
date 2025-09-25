# urbansoccer_server/api/campaigns.py
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import Response # Importante: Usado para retornar o áudio
from pydantic import BaseModel

# --- Seus imports existentes ---
from urbansoccer_server.models import campaign_model, user_character_model
from urbansoccer_server.schemas.campaign_schema import (
    CampaignCreate, 
    CampaignPublic, 
    CampaignList, 
    CampaignUpdate,
    CampaignProgress,
    CampaignWithDetails,
    GameActionPayload,
    PlayResponse # Manteremos este para o endpoint /start
)
from urbansoccer_server.core.auth import get_current_user
from urbansoccer_server.services import (
    campaign_generator,
    game_logic,
    game_narrator,
    tts_provider # Importando o novo serviço de TTS
)

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])

# --- ROTA PARA GERAR OPÇÕES DE CAMPANHA (sem alterações) ---
class CampaignGenerationRequest(BaseModel):
    user_character_id: str

@router.post("/generate-options", status_code=status.HTTP_200_OK)
async def get_campaign_options(
    request: CampaignGenerationRequest,
    current_user: dict = Depends(get_current_user)
):
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


# --- ROTAS DE CRUD DE CAMPANHA (sem alterações) ---

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CampaignPublic)
async def create_new_campaign(
    campaign: CampaignCreate, 
    current_user: dict = Depends(get_current_user)
):
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
    campaigns = await campaign_model.get_campaigns_by_user(current_user["_id"])
    return {"campaigns": campaigns}

@router.get("/active", status_code=status.HTTP_200_OK, response_model=CampaignList)
async def get_active_campaigns(current_user: dict = Depends(get_current_user)):
    campaigns = await campaign_model.get_active_campaigns_by_user(current_user["_id"])
    return {"campaigns": campaigns}

@router.get("/{campaign_id}", status_code=status.HTTP_200_OK, response_model=CampaignPublic)
async def get_campaign(
    campaign_id: str, 
    current_user: dict = Depends(get_current_user)
):
    campaign = await campaign_model.get_campaign_by_user_and_id(current_user["_id"], campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    return campaign

# ... (outras rotas de CRUD como update, delete, etc. permanecem iguais)
@router.get("/{campaign_id}/details", status_code=status.HTTP_200_OK, response_model=CampaignWithDetails)
async def get_campaign_with_details(
    campaign_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Retorna campanha com detalhes do usuário e personagem"""
    campaign = await campaign_model.get_campaign_with_details(campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campanha não encontrada"
        )
    
    # Verifica se a campanha pertence ao usuário atual
    if campaign["userId"] != current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado à esta campanha"
        )
    
    return campaign

@router.patch("/{campaign_id}", status_code=status.HTTP_200_OK, response_model=CampaignPublic)
async def update_campaign(
    campaign_id: str,
    campaign_update: CampaignUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Atualiza dados da campanha"""
    existing_campaign = await campaign_model.get_campaign_by_user_and_id(
        current_user["_id"], campaign_id
    )
    if not existing_campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campanha não encontrada"
        )
    
    update_data = campaign_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum dado para atualizar"
        )
    
    updated_campaign = await campaign_model.update_campaign(campaign_id, update_data)
    return updated_campaign

@router.patch("/{campaign_id}/progress", status_code=status.HTTP_200_OK, response_model=CampaignPublic)
async def update_campaign_progress(
    campaign_id: str,
    progress: CampaignProgress,
    current_user: dict = Depends(get_current_user)
):
    """Atualiza especificamente o progresso da campanha"""
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
    """Marca campanha como abandonada"""
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
    """Marca campanha como completada"""
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
    """Deleta uma campanha"""
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

# --- ROTAS DE LÓGICA DO JOGO ---

@router.get("/{campaign_id}/start", status_code=status.HTTP_200_OK, response_model=PlayResponse)
async def start_game(
    campaign_id: str,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["_id"]
    campaign = await campaign_model.get_campaign_by_user_and_id(user_id, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campanha não encontrada.")

    initial_narration = campaign.get("description", "A jornada começa agora.")
    initial_cards = game_logic.get_initial_cards()
    initial_game_state = {
        "score": "0 - 0",
        "time": 0,
        "commentary": "A bola vai rolar!"
    }
    
    return {
        "narration": initial_narration,
        "availableCards": initial_cards,
        "gameState": initial_game_state
    }


@router.post("/{campaign_id}/play", status_code=status.HTTP_200_OK)
async def play_turn_and_get_audio(
    campaign_id: str,
    payload: GameActionPayload,
    current_user: dict = Depends(get_current_user)
):
    """
    Processa uma ação do jogador, gera a narração em áudio e retorna o áudio.
    """
    user_id = current_user["_id"]
    
    campaign = await campaign_model.get_campaign_by_user_and_id(user_id, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campanha não encontrada.")
    
    character = await user_character_model.get_user_character_with_player(campaign["userCharacterId"], user_id)
    if not character or "player" not in character:
        raise HTTPException(status_code=404, detail="Personagem associado não encontrado.")

    player_stats = character["player"]["stats"]
    player_name = character["characterName"]
    
    outcome_text, _ = game_logic.process_player_action(player_stats, payload.actionId)

    score = campaign.get("progress", {}).get("score", 0)
    if "GOL!" in outcome_text:
        score += 1

    narration_event = {
        "player_name": player_name,
        "action_description": payload.actionId.replace('_', ' '),
        "outcome": outcome_text,
        "score": f"Jogador {score} - 0 Adversário"
    }
    
    # 1. Gera o texto da narração
    narration_text = await game_narrator.narrate_event(narration_event)
    
    # 2. Gera o áudio a partir do texto
    audio_content = await tts_provider.generate_audio_from_text(narration_text)

    if not audio_content:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Não foi possível gerar o áudio da narração."
        )

    # 3. Retorna o conteúdo de áudio diretamente
    return Response(content=audio_content, media_type="audio/wav")