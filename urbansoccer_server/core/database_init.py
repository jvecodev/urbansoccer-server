# urbansoccer_server/core/database_init.py
"""
Inicialização automática do banco de dados com players e campanhas padrão
"""
import logging
import asyncio
import concurrent.futures
from datetime import datetime
from pymongo import AsyncMongoClient
from urbansoccer_server.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Players padrão
DEFAULT_PLAYERS = [
    {
        "name": "Velocista",
        "description": "Um Velocista incrivelmente rápido, capaz de driblar até o vento.",
        "rarity": "unique",
        "stats": {
            "speed": 150,
            "attack": 100,
            "defense": 10,
            "leadership": 5,
            "specialAbility": "Corrida Relâmpago"
        },
        "imageUrl": "https://urban-soccer-bucket.s3.sa-east-1.amazonaws.com/valocista.jpg",
        "isAvailable": True
    },
    {
        "name": "Maestro",
        "description": "Maestro do controle de bola, visão de águia",
        "rarity": "unique",
        "stats": {
            "speed": 50,
            "attack": 140,
            "defense": 80,
            "leadership": 60,
            "specialAbility": "Passe Mágico"
        },
        "imageUrl": "https://urban-soccer-bucket.s3.sa-east-1.amazonaws.com/Maestro.jpg",
        "isAvailable": True
    },
    {
        "name": "O Artilheiro",
        "description": "Artilheiro nato, com fome de gols e vitórias.",
        "rarity": "default",
        "stats": {
            "speed": 80,
            "attack": 150,
            "defense": 10,
            "leadership": 30,
            "specialAbility": "Chute Poderoso"
        },
        "imageUrl": "https://urban-soccer-bucket.s3.sa-east-1.amazonaws.com/Artilheiro.jpg",
        "isAvailable": True
    },
    {
        "name": "Defensor",
        "description": "Um defensor imponente, um muro humano.",
        "rarity": "default",
        "stats": {
            "speed": 50,
            "attack": 10,
            "defense": 150,
            "leadership": 80,
            "specialAbility": "Bloqueio Imbatível"
        },
        "imageUrl": "https://urban-soccer-bucket.s3.sa-east-1.amazonaws.com/defensor.jpg",
        "isAvailable": True
    },
    {
        "name": "Lider",
        "description": "Líder nato, inspira e motiva o time a cada jogo.",
        "rarity": "default",
        "stats": {
            "speed": 30,
            "attack": 20,
            "defense": 140,
            "leadership": 150,
            "specialAbility": "Comando de Equipe"
        },
        "imageUrl": "https://urban-soccer-bucket.s3.sa-east-1.amazonaws.com/Lider.jpg",
        "isAvailable": True
    }
]

# Usuário admin padrão
DEFAULT_ADMIN_USER = {
    "name": "Admin Urban Soccer",
    "email": "admin@urbansoccer.com",
    "password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBdXwtO5S5bq5q"  # hash de "admin123"
}



async def initialize_database():
    """
    Inicializa o banco de dados com dados padrão.
    Nota: Campanhas não são mais criadas automaticamente, 
    pois agora são geradas dinamicamente pela IA baseado nos personagens escolhidos.
    """
    try:

        client = AsyncMongoClient(settings.MONGO_URI)
        db = client[settings.MONGO_DB]
        
        # Collections
        player_collection = db["players"]
        user_collection = db["users"] 
        campaign_collection = db["campaigns"]
        user_character_collection = db["user_characters"]

        try:
            # Índices existentes
            await user_collection.create_index("email", unique=True)
            await campaign_collection.create_index([("userId", 1)])
            await campaign_collection.create_index([("playerId", 1)])
            await player_collection.create_index([("rarity", 1)])
            await player_collection.create_index([("isAvailable", 1)])
            
            # Novos índices para user_characters
            await user_character_collection.create_index([("userId", 1)])
            await user_character_collection.create_index([("playerId", 1)])
            await user_character_collection.create_index([("userId", 1), ("characterName", 1)], unique=True)
            await user_character_collection.create_index([("createdAt", 1)])
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
        
        # Nota: Campanhas agora são geradas dinamicamente pela IA
        # Não criamos mais campanhas padrão no banco

        # Mostrar resumo final
        final_players = await player_collection.count_documents({})
        final_users = await user_collection.count_documents({})
        final_campaigns = await campaign_collection.count_documents({})
        final_characters = await user_character_collection.count_documents({})
        
        logger.info(f"📊 Resumo do banco: {final_players} players, {final_users} usuários, {final_campaigns} campanhas, {final_characters} personagens")
        
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
