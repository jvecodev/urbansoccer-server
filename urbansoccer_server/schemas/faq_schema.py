# urbansoccer_server/schemas/faq_schema.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional

class FAQRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=500, description="A pergunta do usuário para o FAQ")
    conversation_id: Optional[str] = Field(None, description="ID da conversa (opcional para nova conversa)")

class FAQLog(BaseModel):
    id: str = Field(..., alias="_id")
    question: str
    userId: str  
    timestamp: datetime
    answer: Optional[str] = Field(None, description="A resposta do LLM (opcional)")
    conversationId: Optional[str] = Field(None, description="ID da conversa (opcional)")
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class FAQLogList(BaseModel):
    logs: List[FAQLog]

# ======= MODELOS DE CONVERSAÇÃO =======

class Conversation(BaseModel):
    id: str = Field(..., alias="_id")
    title: str
    userId: str
    createdAt: datetime
    updatedAt: datetime
    messageCount: int
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class ConversationList(BaseModel):
    conversations: List[Conversation]

class ConversationCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Título da conversa")

class ConversationUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Novo título da conversa")

class ConversationMessages(BaseModel):
    conversation: Conversation
    messages: List[FAQLog]

class ConversationResponse(BaseModel):
    message: str
    conversation_id: str