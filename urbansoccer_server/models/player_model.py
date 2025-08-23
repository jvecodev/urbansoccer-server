# urbansoccer_server/models/player_model.py
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import List, Optional

from urbansoccer_server.core.config import settings

# Conexão com o banco
client = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.MONGO_DB]
player_collection = db["players"]


async def create_player(player_data: dict) -> dict:
    result = await player_collection.insert_one(player_data)
    new_player = await player_collection.find_one({"_id": result.inserted_id})
    return new_player

async def get_all_players() -> List[dict]:
    return await player_collection.find().to_list(length=None)

async def get_player_by_id(player_id: str) -> Optional[dict]:
    if not ObjectId.is_valid(player_id):
        return None
    return await player_collection.find_one({"_id": ObjectId(player_id)})

async def update_player(player_id: str, data_to_update: dict) -> Optional[dict]:
    if not ObjectId.is_valid(player_id):
        return None
    
    await player_collection.update_one(
        {"_id": ObjectId(player_id)},
        {"$set": data_to_update}
    )
    return await get_player_by_id(player_id)

async def delete_player(player_id: str) -> bool:
    if not ObjectId.is_valid(player_id):
        return False
    
    result = await player_collection.delete_one({"_id": ObjectId(player_id)})
    return result.deleted_count > 0