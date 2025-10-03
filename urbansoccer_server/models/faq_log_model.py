from pymongo import AsyncMongoClient
from datetime import datetime
from typing import List, Dict, Optional
from bson import ObjectId
from urbansoccer_server.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Conexão com o banco
client = AsyncMongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB]
faq_log_collection = db["faq_logs"]
conversations_collection = db["conversations"]

async def create_faq_log(question: str, user_id: str, conversation_id: str = None, answer: str = None) -> Optional[str]:
    """
    Salva uma pergunta feita pelo usuário na coleção de logs do FAQ,
    associando-a ao ID do usuário, conversa e opcionalmente a resposta.
    
    Args:
        question: A pergunta do usuário
        user_id: ID do usuário que fez a pergunta
        conversation_id: ID da conversa (opcional)
        answer: A resposta do LLM (opcional)
        
    Returns:
        O ID do log criado ou None em caso de erro
    """
    try:
        log_entry = {
            "question": question,
            "userId": user_id,  
            "timestamp": datetime.utcnow()
        }
        
        if conversation_id is not None:
            log_entry["conversationId"] = conversation_id
        
        if answer is not None:
            log_entry["answer"] = answer
        
        result = await faq_log_collection.insert_one(log_entry)
        
        if result.inserted_id:
            return str(result.inserted_id)
        else:
            return None
            
    except Exception as e:
        logger.error(f"Erro ao salvar log do FAQ: {e}")
        logger.error(f"Dados do log: question='{question}', user_id='{user_id}', conversation_id='{conversation_id}', answer='{answer[:100] if answer else None}...'")
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

async def update_faq_log_answer(log_id: str, answer: str) -> bool:
    """
    Atualiza um log existente do FAQ com a resposta do LLM.
    
    Args:
        log_id: ID do log a ser atualizado
        answer: A resposta do LLM
        
    Returns:
        True se atualizado com sucesso, False caso contrário
    """
    try:
        # Valida se o log_id é um ObjectId válido
        if not ObjectId.is_valid(log_id):
            logger.warning(f"ID inválido fornecido para atualização: {log_id}")
            return False
        
        result = await faq_log_collection.update_one(
            {"_id": ObjectId(log_id)},
            {"$set": {"answer": answer}}
        )
        
        if result.modified_count > 0:
            logger.info(f"Log do FAQ {log_id} atualizado com resposta")
            return True
        else:
            logger.warning(f"Nenhum log foi atualizado com ID: {log_id}")
            return False
            
    except Exception as e:
        logger.error(f"Erro ao atualizar log do FAQ {log_id} com resposta: {e}")
        return False

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


# ======= FUNÇÕES DE CONVERSAÇÃO =======

async def create_conversation(title: str, user_id: str) -> Optional[str]:
    """
    Cria uma nova conversa para o usuário.
    
    Args:
        title: Título da conversa
        user_id: ID do usuário que criou a conversa
        
    Returns:
        O ID da conversa criada ou None em caso de erro
    """
    try:
        conversation_entry = {
            "title": title,
            "userId": user_id,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "messageCount": 0
        }
        
        result = await conversations_collection.insert_one(conversation_entry)
        
        if result.inserted_id:
            logger.info(f"Conversa criada com sucesso: {result.inserted_id}")
            return str(result.inserted_id)
        else:
            return None
            
    except Exception as e:
        logger.error(f"Erro ao criar conversa: {e}")
        logger.error(f"Dados da conversa: title='{title}', user_id='{user_id}'")
        return None

async def update_conversation_title(conversation_id: str, title: str) -> bool:
    """
    Atualiza o título de uma conversa.
    
    Args:
        conversation_id: ID da conversa
        title: Novo título
        
    Returns:
        True se atualizado com sucesso, False caso contrário
    """
    try:
        if not ObjectId.is_valid(conversation_id):
            logger.warning(f"ID de conversa inválido: {conversation_id}")
            return False
        
        result = await conversations_collection.update_one(
            {"_id": ObjectId(conversation_id)},
            {
                "$set": {
                    "title": title,
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count > 0:
            logger.info(f"Título da conversa {conversation_id} atualizado para: {title}")
            return True
        else:
            logger.warning(f"Nenhuma conversa foi atualizada com ID: {conversation_id}")
            return False
            
    except Exception as e:
        logger.error(f"Erro ao atualizar título da conversa {conversation_id}: {e}")
        return False

async def increment_message_count(conversation_id: str) -> bool:
    """
    Incrementa o contador de mensagens de uma conversa e atualiza o timestamp.
    
    Args:
        conversation_id: ID da conversa
        
    Returns:
        True se atualizado com sucesso, False caso contrário
    """
    try:
        if not ObjectId.is_valid(conversation_id):
            logger.warning(f"ID de conversa inválido: {conversation_id}")
            return False
        
        result = await conversations_collection.update_one(
            {"_id": ObjectId(conversation_id)},
            {
                "$inc": {"messageCount": 1},
                "$set": {"updatedAt": datetime.utcnow()}
            }
        )
        
        return result.modified_count > 0
            
    except Exception as e:
        logger.error(f"Erro ao incrementar contador de mensagens para conversa {conversation_id}: {e}")
        return False

async def get_user_conversations(user_id: str, limit: int = 20) -> List[Dict]:
    """
    Busca as conversas do usuário ordenadas por data de atualização (mais recentes primeiro).
    
    Args:
        user_id: ID do usuário
        limit: Número máximo de conversas a retornar
        
    Returns:
        Lista de conversas do usuário
    """
    try:
        conversations_cursor = conversations_collection.find(
            {"userId": user_id}
        ).sort("updatedAt", -1).limit(limit)
        
        conversations = await conversations_cursor.to_list(length=limit)
        
        # Converte ObjectId para string
        for conversation in conversations:
            if "_id" in conversation:
                conversation["_id"] = str(conversation["_id"])
                
        return conversations
    except Exception as e:
        logger.error(f"Erro ao buscar conversas do usuário {user_id}: {e}")
        return []

async def get_conversation_by_id(conversation_id: str, user_id: str) -> Optional[Dict]:
    """
    Busca uma conversa específica, verificando se pertence ao usuário.
    
    Args:
        conversation_id: ID da conversa
        user_id: ID do usuário
        
    Returns:
        Dados da conversa ou None se não encontrada
    """
    try:
        if not ObjectId.is_valid(conversation_id):
            logger.warning(f"ID de conversa inválido: {conversation_id}")
            return None
        
        conversation = await conversations_collection.find_one({
            "_id": ObjectId(conversation_id),
            "userId": user_id
        })
        
        if conversation:
            conversation["_id"] = str(conversation["_id"])
            
        return conversation
    except Exception as e:
        logger.error(f"Erro ao buscar conversa {conversation_id}: {e}")
        return None

async def get_conversation_messages(conversation_id: str, user_id: str, limit: int = 50) -> List[Dict]:
    """
    Busca todas as mensagens de uma conversa específica.
    
    Args:
        conversation_id: ID da conversa
        user_id: ID do usuário (para verificação de segurança)
        limit: Número máximo de mensagens a retornar
        
    Returns:
        Lista de mensagens da conversa ordenadas por timestamp
    """
    try:
        # Primeiro verifica se a conversa pertence ao usuário
        conversation = await get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            logger.warning(f"Conversa {conversation_id} não encontrada ou não pertence ao usuário {user_id}")
            return []
        
        # Busca as mensagens da conversa
        messages_cursor = faq_log_collection.find(
            {"conversationId": conversation_id}
        ).sort("timestamp", 1).limit(limit)
        
        messages = await messages_cursor.to_list(length=limit)
        
        # Converte ObjectId para string
        for message in messages:
            if "_id" in message:
                message["_id"] = str(message["_id"])
                
        return messages
    except Exception as e:
        logger.error(f"Erro ao buscar mensagens da conversa {conversation_id}: {e}")
        return []

async def delete_conversation(conversation_id: str, user_id: str) -> bool:
    """
    Deleta uma conversa e todas as suas mensagens, verificando se pertence ao usuário.
    
    Args:
        conversation_id: ID da conversa
        user_id: ID do usuário
        
    Returns:
        True se deletada com sucesso, False caso contrário
    """
    try:
        if not ObjectId.is_valid(conversation_id):
            logger.warning(f"ID de conversa inválido: {conversation_id}")
            return False
        
        # Primeiro deleta todas as mensagens da conversa
        await faq_log_collection.delete_many({
            "conversationId": conversation_id
        })
        
        # Depois deleta a conversa
        result = await conversations_collection.delete_one({
            "_id": ObjectId(conversation_id),
            "userId": user_id
        })
        
        if result.deleted_count > 0:
            logger.info(f"Conversa {conversation_id} e suas mensagens deletadas com sucesso pelo usuário {user_id}")
            return True
        else:
            logger.warning(f"Tentativa de deletar conversa inexistente ou sem permissão: {conversation_id} pelo usuário {user_id}")
            return False
            
    except Exception as e:
        logger.error(f"Erro ao deletar conversa {conversation_id}: {e}")
        return False

