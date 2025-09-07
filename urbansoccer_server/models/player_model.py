# urbansoccer_server/models/player_model.py
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import List, Optional
from datetime import datetime

from urbansoccer_server.core.config import settings

# Conexão com o banco
client = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.MONGO_DB]
player_collection = db["players"]

async def create_player(player_data: dict) -> dict:
    """Cria um novo personagem (usado pelo admin para criar personagens padrão)"""
    player_data["createdAt"] = datetime.utcnow()
    result = await player_collection.insert_one(player_data)
    new_player = await player_collection.find_one({"_id": result.inserted_id})
    if new_player and "_id" in new_player:
        new_player["_id"] = str(new_player["_id"])
    return new_player

async def get_all_players() -> List[dict]:
    """Retorna todos os personagens"""
    players = await player_collection.find().to_list(length=None)
    for player in players:
        if "_id" in player:
            player["_id"] = str(player["_id"])
    return players

async def get_available_players() -> List[dict]:
    """Retorna apenas personagens disponíveis para escolha"""
    players = await player_collection.find({"isAvailable": True}).to_list(length=None)
    for player in players:
        if "_id" in player:
            player["_id"] = str(player["_id"])
    return players

async def get_player_by_id(player_id: str) -> Optional[dict]:
    """Busca personagem por ID"""
    if not ObjectId.is_valid(player_id):
        return None
    player = await player_collection.find_one({"_id": ObjectId(player_id)})
    if player and "_id" in player:
        player["_id"] = str(player["_id"])
    return player

async def update_player(player_id: str, data_to_update: dict) -> Optional[dict]:
    """Atualiza dados do personagem (usado pelo admin)"""
    if not ObjectId.is_valid(player_id):
        return None
    
    await player_collection.update_one(
        {"_id": ObjectId(player_id)},
        {"$set": data_to_update}
    )
    return await get_player_by_id(player_id)

async def delete_player(player_id: str) -> bool:
    """Deleta um personagem (usado pelo admin)"""
    if not ObjectId.is_valid(player_id):
        return False
    
    result = await player_collection.delete_one({"_id": ObjectId(player_id)})
    return result.deleted_count > 0

async def get_players_by_rarity(rarity: str) -> List[dict]:
    """Retorna personagens por raridade (default ou unique)"""
    players = await player_collection.find({"rarity": rarity, "isAvailable": True}).to_list(length=None)
    for player in players:
        if "_id" in player:
            player["_id"] = str(player["_id"])
    return players

async def toggle_player_availability(player_id: str, is_available: bool) -> Optional[dict]:
    """Alterna disponibilidade do personagem"""
    if not ObjectId.is_valid(player_id):
        return None
    
    await player_collection.update_one(
        {"_id": ObjectId(player_id)},
        {"$set": {"isAvailable": is_available}}
    )
    return await get_player_by_id(player_id)