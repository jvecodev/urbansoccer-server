# urbansoccer_server/schemas/player_schema.py
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class PlayerBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    position: str = Field(..., description="Ex: Atacante, Defensor, Goleiro")
    skills: Optional[dict] = Field(None, description="Ex: {'chute': 90, 'drible': 85}")

class PlayerCreate(PlayerBase):
    pass

class PlayerUpdate(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None
    skills: Optional[dict] = None

class PlayerPublic(PlayerBase):
    id: str = Field(..., alias="_id")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            "ObjectId": str
        }

class PlayerList(BaseModel):
    players: List[PlayerPublic]