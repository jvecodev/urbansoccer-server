# urbansoccer_server/core/database_init.py
"""
Inicialização automática do banco de dados com players e campanhas padrão
"""
import asyncio
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from urbansoccer_server.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Players padrão
DEFAULT_PLAYERS = [
    {
        "name": "Cavaleiro Sombrio",
        "description": "Um guerreiro formidável que usa o poder das sombras para dominar o campo.",
        "rarity": "unique",
        "stats": {
            "health": 120,
            "attack": 15,
            "defense": 10,
            "specialAbility": "Golpe Fantasma"
        },
        "imageUrl": "https://cdn.urbansoccer.com/players/cavaleiro-sombrio.png",
        "modelUrl": "https://cdn.urbansoccer.com/models/cavaleiro-sombrio.glb",
        "isAvailable": True
    },
    {
        "name": "Arqueiro Élfico",
        "description": "Mestre em precisão e agilidade, nunca erra o alvo.",
        "rarity": "unique",
        "stats": {
            "health": 90,
            "attack": 20,
            "defense": 8,
            "specialAbility": "Tiro Certeiro"
        },
        "imageUrl": "https://cdn.urbansoccer.com/players/arqueiro-elfico.png",
        "modelUrl": "https://cdn.urbansoccer.com/models/arqueiro-elfico.glb",
        "isAvailable": True
    },
    {
        "name": "Paladino Dourado",
        "description": "Protetor dos fracos, sua defesa é imbatível.",
        "rarity": "default",
        "stats": {
            "health": 150,
            "attack": 12,
            "defense": 18,
            "specialAbility": "Escudo Sagrado"
        },
        "imageUrl": "https://cdn.urbansoccer.com/players/paladino-dourado.png",
        "modelUrl": "https://cdn.urbansoccer.com/models/paladino-dourado.glb",
        "isAvailable": True
    },
    {
        "name": "Mago das Chamas",
        "description": "Domina o elemento fogo com maestria devastadora.",
        "rarity": "default",
        "stats": {
            "health": 80,
            "attack": 25,
            "defense": 5,
            "specialAbility": "Bola de Fogo"
        },
        "imageUrl": "https://cdn.urbansoccer.com/players/mago-das-chamas.png",
        "modelUrl": "https://cdn.urbansoccer.com/models/mago-das-chamas.glb",
        "isAvailable": True
    },
    {
        "name": "Ladino Sombrio",
        "description": "Rápido e furtivo, ataca quando menos se espera.",
        "rarity": "default",
        "stats": {
            "health": 100,
            "attack": 18,
            "defense": 7,
            "specialAbility": "Ataque Furtivo"
        },
        "imageUrl": "https://cdn.urbansoccer.com/players/ladino-sombrio.png",
        "modelUrl": "https://cdn.urbansoccer.com/models/ladino-sombrio.glb",
        "isAvailable": True
    }
]

# Usuário admin padrão
DEFAULT_ADMIN_USER = {
    "name": "Admin Urban Soccer",
    "email": "admin@urbansoccer.com",
    "password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBdXwtO5S5bq5q"  # hash de "admin123"
}

# Campanhas padrão
DEFAULT_CAMPAIGNS = [
    {
        "campaignName": "A Jornada do Cavaleiro Sombrio",
        "status": "active",
        "progress": {
            "level": 1,
            "score": 0,
            "currentMission": "O Início da Lenda",
            "inventory": []
        }
    },
    {
        "campaignName": "A Precisão do Arqueiro",
        "status": "active", 
        "progress": {
            "level": 1,
            "score": 0,
            "currentMission": "Primeiro Tiro",
            "inventory": []
        }
    },
    {
        "campaignName": "A Defesa do Paladino",
        "status": "active",
        "progress": {
            "level": 1,
            "score": 0,
            "currentMission": "Proteger os Inocentes",
            "inventory": []
        }
    },
    {
        "campaignName": "O Poder das Chamas",
        "status": "active",
        "progress": {
            "level": 1,
            "score": 0,
            "currentMission": "Dominando o Fogo",
            "inventory": []
        }
    },
    {
        "campaignName": "Nas Sombras do Ladino",
        "status": "active",
        "progress": {
            "level": 1,
            "score": 0,
            "currentMission": "Arte da Furtividade", 
            "inventory": []
        }
    }
]

async def initialize_database():
    """Inicializa o banco de dados com dados padrão"""
    try:

        client = AsyncIOMotorClient(settings.MONGO_URI)
        db = client[settings.MONGO_DB]
        
        # Collections
        player_collection = db["players"]
        user_collection = db["users"] 
        campaign_collection = db["campaigns"]

        try:
            await user_collection.create_index("email", unique=True)
            await campaign_collection.create_index([("userId", 1)])
            await campaign_collection.create_index([("playerId", 1)])
            await player_collection.create_index([("rarity", 1)])
            await player_collection.create_index([("isAvailable", 1)])
        except Exception as e:
            logger.info(f"⚠️ Índices já existem ou erro: {e}")
        
        # Verificar e criar players
        player_count = await player_collection.count_documents({})
        created_players = []
        
        if player_count == 0:
            for player_data in DEFAULT_PLAYERS:
                player_data["createdAt"] = datetime.utcnow()
                result = await player_collection.insert_one(player_data.copy())
                created_players.append(result.inserted_id)
        else:
            existing_players = await player_collection.find({}, {"_id": 1}).to_list(length=5)
            created_players = [player["_id"] for player in existing_players]
        
        admin_user = await user_collection.find_one({"email": DEFAULT_ADMIN_USER["email"]})
        
        if not admin_user:
            DEFAULT_ADMIN_USER["createdAt"] = datetime.utcnow()
            result = await user_collection.insert_one(DEFAULT_ADMIN_USER.copy())
            admin_user_id = result.inserted_id
        else:
            admin_user_id = admin_user["_id"]
        
        # Verificar e criar campanhas
        campaign_count = await campaign_collection.count_documents({})
        
        if campaign_count == 0:
            
            for i, campaign_data in enumerate(DEFAULT_CAMPAIGNS):
                # Associa cada campanha a um player diferente
                if i < len(created_players):
                    campaign_data["userId"] = str(admin_user_id)
                    campaign_data["playerId"] = str(created_players[i])
                    campaign_data["startDate"] = datetime.utcnow()
                    campaign_data["lastPlayedDate"] = datetime.utcnow()
                    
                    result = await campaign_collection.insert_one(campaign_data.copy())

        # Mostrar resumo final
        final_players = await player_collection.count_documents({})
        final_users = await user_collection.count_documents({})
        final_campaigns = await campaign_collection.count_documents({})
        
        logger.info(f"📊 Resumo do banco: {final_players} players, {final_users} usuários, {final_campaigns} campanhas")
        
        await client.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro durante a inicialização do banco: {e}")
        return False

def run_database_initialization():
    """Executa a inicialização do banco de forma síncrona"""
    try:
        # Verifica se já existe um loop em execução
        try:
            loop = asyncio.get_running_loop()
            # Se existe um loop rodando, cria uma task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, initialize_database())
                return future.result()
        except RuntimeError:
            # Não há loop rodando, pode executar normalmente
            return asyncio.run(initialize_database())
    except Exception as e:
        logger.error(f"Erro ao executar inicialização: {e}")
        return False
