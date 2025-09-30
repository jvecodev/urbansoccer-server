# urbansoccer_server/core/database_init.py
import logging
import asyncio
from datetime import datetime
from pymongo import AsyncMongoClient
from urbansoccer_server.core.config import settings

logger = logging.getLogger(__name__)

# Players padrão (continua igual)
DEFAULT_PLAYERS = [
    {
        "name": "Velocista",
        "description": "Um Velocista incrivelmente rápido, capaz de driblar até o vento.",
        "rarity": "unique",
        "stats": { "speed": 150, "attack": 100, "defense": 10, "leadership": 5, "specialAbility": "Corrida Relâmpago" },
        "imageUrl": "https://urban-soccer-bucket.s3.sa-east-1.amazonaws.com/valocista.jpg",
        "isAvailable": True
    },
    {
        "name": "Maestro",
        "description": "Maestro do controle de bola, visão de águia",
        "rarity": "unique",
        "stats": { "speed": 50, "attack": 140, "defense": 80, "leadership": 60, "specialAbility": "Passe Mágico" },
        "imageUrl": "https://urban-soccer-bucket.s3.sa-east-1.amazonaws.com/Maestro.jpg",
        "isAvailable": True
    },
    {
        "name": "O Artilheiro",
        "description": "Artilheiro nato, com fome de gols e vitórias.",
        "rarity": "default",
        "stats": { "speed": 80, "attack": 150, "defense": 10, "leadership": 30, "specialAbility": "Chute Poderoso" },
        "imageUrl": "https://urban-soccer-bucket.s3.sa-east-1.amazonaws.com/Artilheiro.jpg",
        "isAvailable": True
    },
    {
        "name": "Defensor",
        "description": "Um defensor imponente, um muro humano.",
        "rarity": "default",
        "stats": { "speed": 50, "attack": 10, "defense": 150, "leadership": 80, "specialAbility": "Bloqueio Imbatível" },
        "imageUrl": "https://urban-soccer-bucket.s3.sa-east-1.amazonaws.com/defensor.jpg",
        "isAvailable": True
    },
    {
        "name": "Lider",
        "description": "Líder nato, inspira e motiva o time a cada jogo.",
        "rarity": "default",
        "stats": { "speed": 30, "attack": 20, "defense": 140, "leadership": 150, "specialAbility": "Comando de Equipe" },
        "imageUrl": "https://urban-soccer-bucket.s3.sa-east-1.amazonaws.com/Lider.jpg",
        "isAvailable": True
    }
]

# Usuário admin padrão (continua igual)
DEFAULT_ADMIN_USER = {
    "name": "Admin Urban Soccer",
    "email": "admin@urbansoccer.com",
    "password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBdXwtO5S5bq5q"  # hash de "admin123"
}

async def initialize_database():
    """Inicializa o banco de dados com dados padrão."""
    try:
        client = AsyncMongoClient(settings.MONGO_URI)
        db = client[settings.MONGO_DB]
        
        # Collections
        player_collection = db["players"]
        user_collection = db["users"] 
        campaign_collection = db["campaigns"]
        user_character_collection = db["user_characters"]
        faq_log_collection = db["faq_logs"]

        try:
            # Índices
            await user_collection.create_index("email", unique=True)
            await campaign_collection.create_index([("userId", 1)])
            await user_character_collection.create_index([("userId", 1), ("characterName", 1)], unique=True)
            await faq_log_collection.create_index([("userId", 1), ("timestamp", -1)])  # Para buscar por usuário e ordenar por data
            await faq_log_collection.create_index([("timestamp", -1)])  # Para buscar por data
            logger.info("✅ Índices criados com sucesso.")
        except Exception as e:
            logger.info(f"⚠️ Índices já existem ou erro: {e}")
        
        # Verificar e criar players
        if await player_collection.count_documents({}) == 0:
            logger.info("Criando players padrão...")
            for player in DEFAULT_PLAYERS:
                player["createdAt"] = datetime.utcnow()
            await player_collection.insert_many(DEFAULT_PLAYERS)
        
        # Verificar e criar usuário admin
        if not await user_collection.find_one({"email": DEFAULT_ADMIN_USER["email"]}):
            logger.info("Criando usuário admin padrão...")
            admin_user = DEFAULT_ADMIN_USER.copy()
            admin_user["createdAt"] = datetime.utcnow()
            # O hash da senha já está no objeto
            await user_collection.insert_one(admin_user)

        logger.info("🚀 Inicialização do banco de dados concluída.")
        await client.close()
        
    except Exception as e:
        logger.error(f"❌ Erro durante a inicialização do banco: {e}")

# ... (o resto do arquivo, run_database_initialization, continua igual)
def run_database_initialization():
    """Executa a inicialização do banco de forma síncrona"""
    try:
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, initialize_database())
                return future.result()
        except RuntimeError:
            return asyncio.run(initialize_database())
    except Exception as e:
        logger.error(f"Erro ao executar inicialização: {e}")
        return False