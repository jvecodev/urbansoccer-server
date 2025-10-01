from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import StreamingResponse
from urbansoccer_server.services import faq_service
from urbansoccer_server.schemas.faq_schema import (
    FAQRequest, FAQLogList, ConversationList, ConversationCreate, 
    ConversationUpdate, ConversationMessages, ConversationResponse
)
from urbansoccer_server.models import faq_log_model
from urbansoccer_server.core.auth import get_current_user
import logging

logger = logging.getLogger(__name__) 

router = APIRouter(prefix="/faq", tags=["FAQ"])

async def _save_faq_log_with_logging(question: str, user_id: str, conversation_id: str = None) -> str:
    """
    Função auxiliar para salvar FAQ log com logging adequado.
    Retorna o ID do log criado para poder atualizar com a resposta depois.
    """
    try:
        result = await faq_log_model.create_faq_log(question, user_id, conversation_id)
        if result:
            # Incrementa contador de mensagens se faz parte de uma conversa
            if conversation_id:
                await faq_log_model.increment_message_count(conversation_id)
            logger.info(f"FAQ log salvo com sucesso: {result}")
            return result
        else:
            logger.error("Falha ao salvar FAQ log - resultado None")
            return None
    except Exception as e:
        logger.error(f"Erro crítico ao salvar FAQ log: {e}")
        return None

@router.post("/ask/stream", response_class=StreamingResponse)
async def stream_faq_answer(
    request: FAQRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Recebe uma pergunta, cria uma nova conversa se necessário,
    salva imediatamente associada ao usuário e conversa,
    retorna a resposta da LLM em tempo real (streaming) e 
    atualiza o log com a resposta completa ao final.
    """
    user_id = current_user["_id"]
    conversation_id = request.conversation_id
    
    # Se não foi fornecido conversation_id, cria uma nova conversa
    if not conversation_id:
        try:
            # Gera título automaticamente baseado na pergunta
            title = await faq_service.generate_conversation_title(request.question)
            conversation_id = await faq_log_model.create_conversation(title, user_id)
            
            if not conversation_id:
                logger.error("Falha ao criar nova conversa - continuando sem conversa")
                
        except Exception as e:
            logger.error(f"Erro ao criar nova conversa: {e}")
    
    # Salva a pergunta primeiro para obter o log_id
    log_id = await _save_faq_log_with_logging(request.question, user_id, conversation_id)
    
    if not log_id:
        logger.error("Falha ao criar log inicial - continuando sem salvar resposta")

    # Adiciona conversation_id no header da resposta se foi criada uma nova conversa
    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*"
    }
    
    if conversation_id and not request.conversation_id:
        headers["X-Conversation-ID"] = conversation_id

    return StreamingResponse(
        faq_service.ask_faq_stream_and_collect(request.question, log_id),
        media_type="text/plain",
        headers=headers
    )

@router.get("/my-history", response_model=FAQLogList)
async def get_my_faq_history(current_user: dict = Depends(get_current_user)):
    """
    Retorna as 10 perguntas mais recentes feitas pelo usuário logado.
    """
    user_id = current_user["_id"]
    
    try:
        recent_logs = await faq_log_model.get_recent_faq_logs_by_user(user_id=user_id, limit=10)
        return {"logs": recent_logs}
    except Exception as e:
        logger.error(f"Erro ao buscar histórico FAQ para usuário {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar histórico")

@router.delete("/{log_id}")
async def delete_faq_question(
    log_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Deleta uma pergunta específica do histórico do usuário logado.
    """
    user_id = current_user["_id"]
    
    try:
        success = await faq_log_model.delete_faq_log(log_id=log_id, user_id=user_id)
        
        if success:
            return {"message": "Pergunta deletada com sucesso", "deleted_id": log_id}
        else:
            logger.warning(f"Tentativa falhou de deletar pergunta {log_id} pelo usuário {user_id}")
            raise HTTPException(
                status_code=404, 
                detail="Pergunta não encontrada ou você não tem permissão para deletá-la"
            )
            
    except HTTPException:
        raise  # Re-raise HTTPException para manter o status code
    except Exception as e:
        logger.error(f"Erro interno ao deletar pergunta {log_id} para usuário {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao deletar pergunta")


# ======= ENDPOINTS DE CONVERSAÇÃO =======

@router.get("/conversations", response_model=ConversationList)
async def get_user_conversations(current_user: dict = Depends(get_current_user)):
    """
    Lista todas as conversas do usuário logado ordenadas por data de atualização.
    """
    user_id = current_user["_id"]
    
    try:
        conversations = await faq_log_model.get_user_conversations(user_id=user_id, limit=50)
        return {"conversations": conversations}
    except Exception as e:
        logger.error(f"Erro ao buscar conversas para usuário {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar conversas")

@router.post("/conversations", response_model=ConversationResponse)
async def create_new_conversation(
    request: ConversationCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Cria uma nova conversa com o título fornecido.
    """
    user_id = current_user["_id"]
    
    try:
        conversation_id = await faq_log_model.create_conversation(request.title, user_id)
        
        if conversation_id:
            return {
                "message": "Conversa criada com sucesso",
                "conversation_id": conversation_id
            }
        else:
            raise HTTPException(status_code=500, detail="Falha ao criar conversa")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro interno ao criar conversa para usuário {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao criar conversa")

@router.get("/conversations/{conversation_id}", response_model=ConversationMessages)
async def get_conversation_with_messages(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Busca uma conversa específica com todas as suas mensagens.
    """
    user_id = current_user["_id"]
    
    try:
        # Busca a conversa
        conversation = await faq_log_model.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversa não encontrada")
        
        # Busca as mensagens da conversa
        messages = await faq_log_model.get_conversation_messages(conversation_id, user_id)
        
        return {
            "conversation": conversation,
            "messages": messages
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro interno ao buscar conversa {conversation_id} para usuário {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar conversa")

@router.put("/conversations/{conversation_id}")
async def update_conversation_title(
    conversation_id: str,
    request: ConversationUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Atualiza o título de uma conversa.
    """
    user_id = current_user["_id"]
    
    try:
        # Verifica se a conversa pertence ao usuário
        conversation = await faq_log_model.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversa não encontrada")
        
        success = await faq_log_model.update_conversation_title(conversation_id, request.title)
        
        if success:
            return {"message": "Título da conversa atualizado com sucesso"}
        else:
            raise HTTPException(status_code=500, detail="Falha ao atualizar título da conversa")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro interno ao atualizar conversa {conversation_id} para usuário {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao atualizar conversa")

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Deleta uma conversa e todas as suas mensagens.
    """
    user_id = current_user["_id"]
    
    try:
        success = await faq_log_model.delete_conversation(conversation_id, user_id)
        
        if success:
            return {"message": "Conversa deletada com sucesso", "deleted_id": conversation_id}
        else:
            raise HTTPException(
                status_code=404, 
                detail="Conversa não encontrada ou você não tem permissão para deletá-la"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro interno ao deletar conversa {conversation_id} para usuário {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao deletar conversa")



    