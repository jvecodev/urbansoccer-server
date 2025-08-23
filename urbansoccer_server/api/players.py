# urbansoccer_server/api/players.py
from fastapi import APIRouter, HTTPException, status
from urbansoccer_server.models import player_model
from urbansoccer_server.schemas.player_schema import PlayerCreate, PlayerPublic, PlayerList, PlayerUpdate

router = APIRouter(prefix="/players", tags=["Players"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PlayerPublic)
async def create_new_player(player: PlayerCreate):
    player_dict = player.model_dump()
    created_player = await player_model.create_player(player_dict)
    return created_player

@router.get("/", status_code=status.HTTP_200_OK, response_model=PlayerList)
async def get_all_players():
    players = await player_model.get_all_players()
    return {"players": players}

@router.get("/{player_id}", status_code=status.HTTP_200_OK, response_model=PlayerPublic)
async def get_player(player_id: str):
    player = await player_model.get_player_by_id(player_id)
    if player is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jogador não encontrado")
    return player

@router.patch("/{player_id}", status_code=status.HTTP_200_OK, response_model=PlayerPublic)
async def update_existing_player(player_id: str, player_update: PlayerUpdate):
    update_data = player_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nenhum dado para atualizar")
        
    updated_player = await player_model.update_player(player_id, update_data)
    if updated_player is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jogador não encontrado")
    return updated_player

@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_player(player_id: str):
    success = await player_model.delete_player(player_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jogador não encontrado")