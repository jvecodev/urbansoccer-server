# urbansoccer_server/models/user_character_model.py
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import List, Optional
from datetime import datetime

from urbansoccer_server.core.config import settings
from urbansoccer_server.models.player_model import get_player_by_id

# Conexão com o banco
client = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.MONGO_DB]
user_character_collection = db["user_characters"]

async def create_user_character(user_id: str, character_data: dict) -> Optional[dict]:

    try:
        # Verifica se o usuário já tem um personagem com esse nome
        existing_character = await user_character_collection.find_one({
            "userId": user_id,
            "characterName": character_data["characterName"]
        })
        
        if existing_character:
            return None  # Nome já em uso pelo mesmo usuário
        
        # Cria o personagem
        new_character = {
            "characterName": character_data["characterName"],
            "playerId": character_data["playerId"],
            "userId": user_id,
            "createdAt": datetime.utcnow()
        }
        
        result = await user_character_collection.insert_one(new_character)
        created_character = await user_character_collection.find_one({"_id": result.inserted_id})
        
        if created_character and "_id" in created_character:
            created_character["_id"] = str(created_character["_id"])
        
        return created_character
        
    except Exception as e:
        return None

async def get_user_characters(user_id: str) -> List[dict]:
    """
    Retorna todos os personagens de um usuário
    
    Args:
        user_id: ID do usuário
    
    Returns:
        List[dict]: Lista de personagens do usuário
    """
    try:
        characters = await user_character_collection.find({"userId": user_id}).to_list(length=None)
        
        for character in characters:
            if "_id" in character:
                character["_id"] = str(character["_id"])
        
        return characters
        
    except Exception as e:
        return []

async def get_user_character_by_id(character_id: str, user_id: str = None) -> Optional[dict]:
    """
    Retorna um personagem específico
    
    Args:
        character_id: ID do personagem
        user_id: ID do usuário (opcional, para validação)
    
    Returns:
        dict: Personagem encontrado ou None
    """
    try:
        query = {"_id": ObjectId(character_id)}
        if user_id:
            query["userId"] = user_id
        
        character = await user_character_collection.find_one(query)
        
        if character and "_id" in character:
            character["_id"] = str(character["_id"])
        
        return character
        
    except Exception as e:
        return None

async def update_user_character(character_id: str, user_id: str, update_data: dict) -> Optional[dict]:
    """
    Atualiza um personagem do usuário
    
    Args:
        character_id: ID do personagem
        user_id: ID do usuário
        update_data: Dados para atualização
    
    Returns:
        dict: Personagem atualizado ou None
    """
    try:
        
        # Verifica se o character_id é um ObjectId válido
        try:
            ObjectId(character_id)
        except Exception as e:
            return None
        
        # Verifica se o personagem existe antes de tentar atualizar
        existing_character = await user_character_collection.find_one({
            "_id": ObjectId(character_id), 
            "userId": user_id
        })
        
        if not existing_character:
            return None
        
        
        # Remove campos que não devem ser atualizados diretamente
        forbidden_fields = ["_id", "userId", "playerId", "createdAt"]
        update_data = {k: v for k, v in update_data.items() if k not in forbidden_fields}
        
        if not update_data:
            return None
        
        # Verifica se está tentando alterar o nome para um já existente
        if "characterName" in update_data:
            duplicate_check = await user_character_collection.find_one({
                "userId": user_id,
                "characterName": update_data["characterName"],
                "_id": {"$ne": ObjectId(character_id)}
            })
            if duplicate_check:
                return None
        
        
        result = await user_character_collection.update_one(
            {"_id": ObjectId(character_id), "userId": user_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            # Busca o documento atualizado diretamente
            updated_character = await user_character_collection.find_one({
                "_id": ObjectId(character_id), 
                "userId": user_id
            })
            
            if updated_character and "_id" in updated_character:
                updated_character["_id"] = str(updated_character["_id"])
            
            return updated_character
        elif result.matched_count > 0:
            # Retorna o documento mesmo se não foi modificado
            current_character = await user_character_collection.find_one({
                "_id": ObjectId(character_id), 
                "userId": user_id
            })
            
            if current_character and "_id" in current_character:
                current_character["_id"] = str(current_character["_id"])
            
            return current_character
        else:
            return None
        
    except Exception as e:
        return None

async def delete_user_character(character_id: str, user_id: str) -> bool:
    """
    Deleta um personagem do usuário
    
    Args:
        character_id: ID do personagem
        user_id: ID do usuário
    
    Returns:
        bool: True se deletado com sucesso
    """
    try:
        result = await user_character_collection.delete_one({
            "_id": ObjectId(character_id), 
            "userId": user_id
        })
        
        return result.deleted_count > 0
        
    except Exception as e:
        return False

async def get_user_characters_with_players(user_id: str) -> List[dict]:
    """
    Retorna todos os personagens de um usuário com informações completas dos players
    
    Args:
        user_id: ID do usuário
    
    Returns:
        List[dict]: Lista de personagens com dados dos players
    """
    try:
        characters = await user_character_collection.find({"userId": user_id}).to_list(length=None)
        
        characters_with_players = []
        
        for character in characters:
            if "_id" in character:
                character["_id"] = str(character["_id"])
            
            # Busca as informações do player
            player = await get_player_by_id(character["playerId"])
            
            if player:
                character_with_player = {
                    **character,
                    "player": player
                }
                characters_with_players.append(character_with_player)
        
        return characters_with_players
        
    except Exception as e:
        return []

async def get_user_character_with_player(character_id: str, user_id: str = None) -> Optional[dict]:
    """
    Retorna um personagem específico com informações do player
    
    Args:
        character_id: ID do personagem
        user_id: ID do usuário (opcional, para validação)
    
    Returns:
        dict: Personagem com dados do player ou None
    """
    try:
        character = await get_user_character_by_id(character_id, user_id)
        if not character:
            return None
        
        # Busca as informações do player
        player = await get_player_by_id(character["playerId"])
        if not player:
            return None
        
        return {
            **character,
            "player": player
        }
        
    except Exception as e:
        print(f"Erro ao buscar personagem com player: {e}")
        return None
