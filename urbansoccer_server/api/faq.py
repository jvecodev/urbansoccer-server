from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from urbansoccer_server.services import faq_service
from urbansoccer_server.schemas.faq_schema import FAQRequest, FAQLogList
from urbansoccer_server.models import faq_log_model
from urbansoccer_server.core.auth import get_current_user 

router = APIRouter(prefix="/faq", tags=["FAQ"])

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
    background_tasks.add_task(faq_log_model.create_faq_log, request.question, user_id)

    return StreamingResponse(
        faq_service.ask_faq_stream(request.question),
        media_type="text/event-stream"
    )

@router.get("/my-history", response_model=FAQLogList)
async def get_my_faq_history(current_user: dict = Depends(get_current_user)):
    """
    Retorna as 10 perguntas mais recentes feitas pelo usuário logado.
    """
    user_id = current_user["_id"]
    recent_logs = await faq_log_model.get_recent_faq_logs_by_user(user_id=user_id, limit=10)
    return {"logs": recent_logs}