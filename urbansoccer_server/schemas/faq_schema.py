# urbansoccer_server/schemas/faq_schema.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List

class FAQRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=500, description="A pergunta do usuário para o FAQ")

class FAQLog(BaseModel):
    id: str = Field(..., alias="_id")
    question: str
    userId: str  
    timestamp: datetime
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class FAQLogList(BaseModel):
    logs: List[FAQLog]