# urbansoccer_server/models/campaign_model.py
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import List, Optional
from datetime import datetime

from urbansoccer_server.core.config import settings

# Conexão com o banco
client = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.MONGO_DB]
campaign_collection = db["campaigns"]

async def create_campaign(user_id: str, campaign_data: dict) -> dict:
    """Cria uma nova campanha para o usuário"""
    campaign_data["userId"] = user_id
    campaign_data["startDate"] = datetime.utcnow()
    campaign_data["lastPlayedDate"] = datetime.utcnow()
    campaign_data["status"] = "active"
    
    # Define progresso inicial se não fornecido
    if "progress" not in campaign_data:
        campaign_data["progress"] = {
            "level": 1,
            "score": 0,
            "currentMission": "Primeira Missão",
            "inventory": []
        }
    
    result = await campaign_collection.insert_one(campaign_data)
    new_campaign = await campaign_collection.find_one({"_id": result.inserted_id})
    if new_campaign and "_id" in new_campaign:
        new_campaign["_id"] = str(new_campaign["_id"])
    return new_campaign

async def get_campaigns_by_user(user_id: str) -> List[dict]:
    """Retorna todas as campanhas de um usuário"""
    campaigns = await campaign_collection.find({"userId": user_id}).to_list(length=None)
    for campaign in campaigns:
        if "_id" in campaign:
            campaign["_id"] = str(campaign["_id"])
    return campaigns

async def get_active_campaigns_by_user(user_id: str) -> List[dict]:
    """Retorna campanhas ativas de um usuário"""
    campaigns = await campaign_collection.find({
        "userId": user_id, 
        "status": "active"
    }).to_list(length=None)
    for campaign in campaigns:
        if "_id" in campaign:
            campaign["_id"] = str(campaign["_id"])
    return campaigns

async def get_campaign_by_id(campaign_id: str) -> Optional[dict]:
    """Busca campanha por ID"""
    if not ObjectId.is_valid(campaign_id):
        return None
    campaign = await campaign_collection.find_one({"_id": ObjectId(campaign_id)})
    if campaign and "_id" in campaign:
        campaign["_id"] = str(campaign["_id"])
    return campaign

async def get_campaign_by_user_and_id(user_id: str, campaign_id: str) -> Optional[dict]:
    """Busca campanha por ID e verifica se pertence ao usuário"""
    if not ObjectId.is_valid(campaign_id):
        return None
    campaign = await campaign_collection.find_one({
        "_id": ObjectId(campaign_id),
        "userId": user_id
    })
    if campaign and "_id" in campaign:
        campaign["_id"] = str(campaign["_id"])
    return campaign

async def update_campaign(campaign_id: str, data_to_update: dict) -> Optional[dict]:
    """Atualiza dados da campanha"""
    if not ObjectId.is_valid(campaign_id):
        return None
    
    # Atualiza a data da última jogada automaticamente
    data_to_update["lastPlayedDate"] = datetime.utcnow()
    
    await campaign_collection.update_one(
        {"_id": ObjectId(campaign_id)},
        {"$set": data_to_update}
    )
    return await get_campaign_by_id(campaign_id)

async def update_campaign_progress(campaign_id: str, progress_data: dict) -> Optional[dict]:
    """Atualiza especificamente o progresso da campanha"""
    if not ObjectId.is_valid(campaign_id):
        return None
    
    update_data = {
        "progress": progress_data,
        "lastPlayedDate": datetime.utcnow()
    }
    
    await campaign_collection.update_one(
        {"_id": ObjectId(campaign_id)},
        {"$set": update_data}
    )
    return await get_campaign_by_id(campaign_id)

async def delete_campaign(campaign_id: str) -> bool:
    """Deleta uma campanha"""
    if not ObjectId.is_valid(campaign_id):
        return False
    
    result = await campaign_collection.delete_one({"_id": ObjectId(campaign_id)})
    return result.deleted_count > 0

async def abandon_campaign(campaign_id: str) -> Optional[dict]:
    """Marca uma campanha como abandonada"""
    return await update_campaign(campaign_id, {"status": "abandoned"})

async def complete_campaign(campaign_id: str) -> Optional[dict]:
    """Marca uma campanha como completada"""
    return await update_campaign(campaign_id, {"status": "completed"})

async def get_campaigns_by_player(player_id: str) -> List[dict]:
    """Retorna todas as campanhas que usam um personagem específico"""
    campaigns = await campaign_collection.find({"playerId": player_id}).to_list(length=None)
    for campaign in campaigns:
        if "_id" in campaign:
            campaign["_id"] = str(campaign["_id"])
    return campaigns

async def check_user_has_active_campaign_with_player(user_id: str, player_id: str) -> bool:
    """Verifica se o usuário já tem uma campanha ativa com este personagem"""
    campaign = await campaign_collection.find_one({
        "userId": user_id,
        "playerId": player_id,
        "status": "active"
    })
    return campaign is not None

async def get_campaign_with_details(campaign_id: str) -> Optional[dict]:
    """Retorna campanha com detalhes do usuário e personagem"""
    if not ObjectId.is_valid(campaign_id):
        return None
    
    pipeline = [
        {"$match": {"_id": ObjectId(campaign_id)}},
        {
            "$lookup": {
                "from": "users",
                "localField": "userId",
                "foreignField": "_id",
                "as": "user_details"
            }
        },
        {
            "$lookup": {
                "from": "players", 
                "localField": "playerId",
                "foreignField": "_id",
                "as": "player_details"
            }
        },
        {
            "$project": {
                "_id": 1,
                "userId": 1,
                "playerId": 1,
                "campaignName": 1,
                "status": 1,
                "progress": 1,
                "startDate": 1,
                "lastPlayedDate": 1,
                "user": {"$arrayElemAt": ["$user_details", 0]},
                "player": {"$arrayElemAt": ["$player_details", 0]}
            }
        }
    ]
    
    cursor = campaign_collection.aggregate(pipeline)
    campaign = await cursor.to_list(length=1)
    
    if campaign:
        campaign = campaign[0]
        if "_id" in campaign:
            campaign["_id"] = str(campaign["_id"])
        # Remove senha do usuário se existir
        if campaign.get("user") and "password" in campaign["user"]:
            del campaign["user"]["password"]
        return campaign
    
    return None
