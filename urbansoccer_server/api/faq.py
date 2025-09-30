from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import StreamingResponse
from urbansoccer_server.services import faq_service
from urbansoccer_server.schemas.faq_schema import FAQRequest, FAQLogList
from urbansoccer_server.models import faq_log_model
from urbansoccer_server.core.auth import get_current_user
import logging

logger = logging.getLogger(__name__) 

router = APIRouter(prefix="/faq", tags=["FAQ"])

async def _save_faq_log_with_logging(question: str, user_id: str):
    """
    Função auxiliar para salvar FAQ log com logging adequado.
    """
    try:
        result = await faq_log_model.create_faq_log(question, user_id)
        if result:
            logger.info(f"FAQ log salvo com sucesso: {result}")
        else:
            logger.error("Falha ao salvar FAQ log - resultado None")
    except Exception as e:
        logger.error(f"Erro crítico ao salvar FAQ log: {e}")

@router.post("/ask/stream", response_class=StreamingResponse)
async def stream_faq_answer(
    request: FAQRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Recebe uma pergunta, salva em background associada ao usuário
    e retorna a resposta da LLM em tempo real (streaming).
    """
    user_id = current_user["_id"]
    
    background_tasks.add_task(_save_faq_log_with_logging, request.question, user_id)

    return StreamingResponse(
        faq_service.ask_faq_stream(request.question),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        }
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



    