# urbansoccer_server/api/user_character.py
from fastapi import APIRouter, HTTPException, status, Depends

from urbansoccer_server.models import user_character_model
from urbansoccer_server.schemas.user_character_schema import (
    UserCharacterCreate,
    UserCharacterPublic,
    UserCharacterList,
    UserCharacterUpdate,
    UserCharacterWithPlayer,
    UserCharacterWithPlayerList
)
from urbansoccer_server.core.auth import get_current_user

router = APIRouter(tags=["User Characters"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserCharacterPublic)
async def create_character(
    character_data: UserCharacterCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Cria um novo personagem nomeado pelo usuário
    """
    user_id = current_user["_id"]
    
    character_dict = character_data.model_dump()
    created_character = await user_character_model.create_user_character(user_id, character_dict)
    
    if not created_character:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível criar o personagem. Verifique se o player existe e se o nome não está em uso."
        )
    
    return created_character

@router.get("/", status_code=status.HTTP_200_OK, response_model=UserCharacterWithPlayerList)
async def get_my_characters(current_user: dict = Depends(get_current_user)):
    """
    Retorna todos os personagens do usuário atual com informações completas dos players
    """
    user_id = current_user["_id"]
    characters = await user_character_model.get_user_characters_with_players(user_id)
    
    return {"characters": characters}

@router.get("/{character_id}", status_code=status.HTTP_200_OK, response_model=UserCharacterWithPlayer)
async def get_character(
    character_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna um personagem específico do usuário com informações completas do player
    """
    user_id = current_user["_id"]
    character = await user_character_model.get_user_character_with_player(character_id, user_id)
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personagem não encontrado"
        )
    
    return character

@router.patch("/{character_id}", status_code=status.HTTP_200_OK, response_model=UserCharacterPublic)
async def update_character(
    character_id: str,
    character_update: UserCharacterUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Atualiza o nome de um personagem do usuário
    """
    user_id = current_user["_id"]
    update_data = character_update.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum dado para atualizar"
        )
    
    updated_character = await user_character_model.update_user_character(character_id, user_id, update_data)
    
    if not updated_character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personagem não encontrado ou nome já está em uso"
        )
    
    return updated_character

@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(
    character_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Deleta um personagem do usuário
    """
    user_id = current_user["_id"]
    success = await user_character_model.delete_user_character(character_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personagem não encontrado"
        )