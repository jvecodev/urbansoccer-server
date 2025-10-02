from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from urbansoccer_server.services import tts_service
from urbansoccer_server.schemas.narration_schema import NarrationRequest

router = APIRouter(prefix="/narration", tags=["Narration"])

@router.post("/speak", response_class=StreamingResponse)
async def get_speech_audio(request: NarrationRequest):
    """
    Recebe um texto e retorna o áudio da narração como um stream.
    """
    try:
        audio_stream = await tts_service.text_to_speech_stream(request.text)
        if not audio_stream:
            raise HTTPException(status_code=500, detail="Falha ao gerar o stream de áudio.")

        # Retorna o áudio como um stream mp3
        return StreamingResponse(audio_stream, media_type="audio/mpeg")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))