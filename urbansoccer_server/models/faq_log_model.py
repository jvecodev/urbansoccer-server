from pymongo import AsyncMongoClient
from datetime import datetime
from typing import List, Dict
from bson import ObjectId
from urbansoccer_server.core.config import settings

# Conexão com o banco
client = AsyncMongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB]
faq_log_collection = db["faq_logs"]

async def create_faq_log(question: str, user_id: str):
    """
    Salva uma pergunta feita pelo usuário na coleção de logs do FAQ,
    associando-a ao ID do usuário.
    """
    try:
        log_entry = {
            "question": question,
            "userId": user_id,  
            "timestamp": datetime.utcnow()
        }
        await faq_log_collection.insert_one(log_entry)
    except Exception as e:
        print(f"Erro ao salvar log do FAQ: {e}")

async def get_recent_faq_logs_by_user(user_id: str, limit: int = 10) -> List[Dict]:
    """
    Busca as N perguntas mais recentes feitas por um usuário específico.
    """
    try:
        logs_cursor = faq_log_collection.find(
            {"userId": user_id} # Filtra pelo ID do usuário
        ).sort("timestamp", -1).limit(limit)
        
        recent_logs = await logs_cursor.to_list(length=limit)
        
        for log in recent_logs:
            if "_id" in log:
                log["_id"] = str(log["_id"])
                
        return recent_logs
    except Exception as e:
        print(f"Erro ao buscar logs do FAQ do usuário: {e}")
        return []