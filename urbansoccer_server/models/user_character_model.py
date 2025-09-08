# urbansoccer_server/models/user_character_model.py
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import List, Optional
from datetime import datetime

from urbansoccer_server.core.config import settings

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
        print(f"Erro ao criar personagem: {e}")
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
        print(f"Erro ao buscar personagens do usuário: {e}")
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
        print(f"Erro ao buscar personagem: {e}")
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
        # Remove campos que não devem ser atualizados diretamente
        forbidden_fields = ["_id", "userId", "playerId", "createdAt"]
        update_data = {k: v for k, v in update_data.items() if k not in forbidden_fields}
        
        if not update_data:
            return None
        
        # Verifica se está tentando alterar o nome para um já existente
        if "characterName" in update_data:
            existing_character = await user_character_collection.find_one({
                "userId": user_id,
                "characterName": update_data["characterName"],
                "_id": {"$ne": ObjectId(character_id)}
            })
            if existing_character:
                return None  # Nome já em uso
        
        result = await user_character_collection.update_one(
            {"_id": ObjectId(character_id), "userId": user_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return await get_user_character_by_id(character_id, user_id)
        
        return None
        
    except Exception as e:
        print(f"Erro ao atualizar personagem: {e}")
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
        print(f"Erro ao deletar personagem: {e}")
        return False
