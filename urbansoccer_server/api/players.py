# urbansoccer_server/api/players.py
from fastapi import APIRouter, HTTPException, status, Depends
from urbansoccer_server.models import player_model
from urbansoccer_server.schemas.player_schema import PlayerCreate, PlayerPublic, PlayerList, PlayerUpdate
from urbansoccer_server.core.auth import get_current_user

router = APIRouter(prefix="/players", tags=["Players"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PlayerPublic)
async def create_new_player(
    player: PlayerCreate, 
    current_user: dict = Depends(get_current_user)
):
    """Cria um novo personagem (apenas para admins)"""
    player_dict = player.model_dump()
    created_player = await player_model.create_player(player_dict)
    return created_player

@router.get("/", status_code=status.HTTP_200_OK, response_model=PlayerList)
async def get_all_players():
    """Retorna todos os personagens (público - não requer autenticação)"""
    players = await player_model.get_all_players()
    return {"players": players}

@router.get("/available", status_code=status.HTTP_200_OK, response_model=PlayerList)
async def get_available_players():
    """Retorna apenas personagens disponíveis para escolha"""
    players = await player_model.get_available_players()
    return {"players": players}

@router.get("/rarity/{rarity}", status_code=status.HTTP_200_OK, response_model=PlayerList)
async def get_players_by_rarity(rarity: str):
    """Retorna personagens por raridade (default ou unique)"""
    if rarity not in ["default", "unique"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Raridade deve ser 'default' ou 'unique'"
        )
    
    players = await player_model.get_players_by_rarity(rarity)
    return {"players": players}

@router.get("/{player_id}", status_code=status.HTTP_200_OK, response_model=PlayerPublic)
async def get_player(player_id: str):
    """Retorna um personagem específico"""
    player = await player_model.get_player_by_id(player_id)
    if player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Personagem não encontrado"
        )
    return player

@router.patch("/{player_id}", status_code=status.HTTP_200_OK, response_model=PlayerPublic)
async def update_existing_player(
    player_id: str, 
    player_update: PlayerUpdate, 
    current_user: dict = Depends(get_current_user)
):
    """Atualiza dados do personagem (apenas para admins)"""
    update_data = player_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Nenhum dado para atualizar"
        )
        
    updated_player = await player_model.update_player(player_id, update_data)
    if updated_player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Personagem não encontrado"
        )
    return updated_player

@router.patch("/{player_id}/availability", status_code=status.HTTP_200_OK, response_model=PlayerPublic)
async def toggle_player_availability(
    player_id: str, 
    is_available: bool,
    current_user: dict = Depends(get_current_user)
):
    """Altera a disponibilidade do personagem (apenas para admins)"""
    updated_player = await player_model.toggle_player_availability(player_id, is_available)
    if updated_player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Personagem não encontrado"
        )
    return updated_player

@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_player(
    player_id: str, 
    current_user: dict = Depends(get_current_user)
):
    """Deleta um personagem (apenas para admins)"""
    success = await player_model.delete_player(player_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Personagem não encontrado"
        )