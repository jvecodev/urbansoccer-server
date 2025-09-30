from pymongo import AsyncMongoClient
from datetime import datetime
from typing import List, Dict, Optional
from bson import ObjectId
from urbansoccer_server.core.config import settings
import logging

# Configuração do logging
logger = logging.getLogger(__name__)

# Conexão com o banco
client = AsyncMongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB]
faq_log_collection = db["faq_logs"]

async def create_faq_log(question: str, user_id: str) -> Optional[str]:
    """
    Salva uma pergunta feita pelo usuário na coleção de logs do FAQ,
    associando-a ao ID do usuário.
    
    Args:
        question: A pergunta do usuário
        user_id: ID do usuário que fez a pergunta
        
    Returns:
        O ID do log criado ou None em caso de erro
    """
    try:
        log_entry = {
            "question": question,
            "userId": user_id,  
            "timestamp": datetime.utcnow()
        }
        
        result = await faq_log_collection.insert_one(log_entry)
        
        if result.inserted_id:
            return str(result.inserted_id)
        else:
            return None
            
    except Exception as e:
        logger.error(f"Erro ao salvar log do FAQ: {e}")
        logger.error(f"Dados do log: question='{question}', user_id='{user_id}'")
        return None

async def get_recent_faq_logs_by_user(user_id: str, limit: int = 10) -> List[Dict]:
    """
    Busca as N perguntas mais recentes feitas por um usuário específico.
    
    Args:
        user_id: ID do usuário para filtrar os logs
        limit: Número máximo de logs a retornar
        
    Returns:
        Lista de logs do FAQ do usuário
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
        logger.error(f"Erro ao buscar logs do FAQ do usuário {user_id}: {e}")
        return []

async def delete_faq_log(log_id: str, user_id: str) -> bool:
    """
    Deleta uma pergunta específica do FAQ, verificando se pertence ao usuário.
    
    Args:
        log_id: ID do log a ser deletado
        user_id: ID do usuário que está tentando deletar
        
    Returns:
        True se deletado com sucesso, False caso contrário
    """
    try:
        # Valida se o log_id é um ObjectId válido
        if not ObjectId.is_valid(log_id):
            logger.warning(f"ID inválido fornecido: {log_id}")
            return False
        
        # Deleta apenas se o log pertence ao usuário
        result = await faq_log_collection.delete_one({
            "_id": ObjectId(log_id),
            "userId": user_id
        })
        
        if result.deleted_count > 0:
            logger.info(f"Log do FAQ {log_id} deletado com sucesso pelo usuário {user_id}")
            return True
        else:
            logger.warning(f"Tentativa de deletar log inexistente ou sem permissão: {log_id} pelo usuário {user_id}")
            return False
            
    except Exception as e:
        logger.error(f"Erro ao deletar log do FAQ {log_id}: {e}")
        return False

