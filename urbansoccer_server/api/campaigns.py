# urbansoccer_server/api/campaigns.py
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

# Imports dos seus models e schemas existentes
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

# Import do novo serviço de IA que criamos
from urbansoccer_server.services import campaign_generator

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])

# --- ROTA NOVA PARA GERAR CAMPANHAS COM IA ---

class CampaignGenerationRequest(BaseModel):
    """Schema para o corpo da requisição da geração de campanhas."""
    user_character_id: str

@router.post("/generate-options", status_code=status.HTTP_200_OK)
async def get_campaign_options(
    request: CampaignGenerationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Gera 4 opções de campanhas iniciais usando IA, baseado no personagem do usuário.
    """
    user_id = current_user["_id"]
    
    # 1. Busca o personagem do usuário para obter os detalhes do player associado
    user_char_with_player = await user_character_model.get_user_character_with_player(request.user_character_id, user_id)

    if not user_char_with_player or "player" not in user_char_with_player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personagem do usuário não encontrado."
        )

    # 2. Envia os detalhes do player para o serviço de IA gerar as opções
    player_details = user_char_with_player["player"]
    options = await campaign_generator.generate_campaign_options(player_details)

    # 3. Retorna as opções para o frontend
    return {"options": options}


# --- ROTAS EXISTENTES (sem alteração na lógica) ---

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CampaignPublic)
async def create_new_campaign(
    campaign: CampaignCreate, 
    current_user: dict = Depends(get_current_user)
):
    """Cria uma nova campanha para o usuário autenticado"""
    # Verifica se o personagem existe e está disponível
    player = await player_model.get_player_by_id(campaign.playerId)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personagem não encontrado"
        )
    
    if not player.get("isAvailable", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Personagem não está disponível para seleção"
        )
    
    # Verifica se o usuário já tem uma campanha ativa com este personagem
    has_active_campaign = await campaign_model.check_user_has_active_campaign_with_player(
        current_user["_id"], campaign.playerId
    )
    
    if has_active_campaign:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você já possui uma campanha ativa com este personagem"
        )
    
    campaign_dict = campaign.model_dump()
    created_campaign = await campaign_model.create_campaign(current_user["_id"], campaign_dict)
    return created_campaign

@router.get("/", status_code=status.HTTP_200_OK, response_model=CampaignList)
async def get_user_campaigns(current_user: dict = Depends(get_current_user)):
    """Retorna todas as campanhas do usuário autenticado"""
    campaigns = await campaign_model.get_campaigns_by_user(current_user["_id"])
    return {"campaigns": campaigns}

@router.get("/active", status_code=status.HTTP_200_OK, response_model=CampaignList)
async def get_active_campaigns(current_user: dict = Depends(get_current_user)):
    """Retorna campanhas ativas do usuário autenticado"""
    campaigns = await campaign_model.get_active_campaigns_by_user(current_user["_id"])
    return {"campaigns": campaigns}

@router.get("/{campaign_id}", status_code=status.HTTP_200_OK, response_model=CampaignPublic)
async def get_campaign(
    campaign_id: str, 
    current_user: dict = Depends(get_current_user)
):
    """Retorna uma campanha específica do usuário"""
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