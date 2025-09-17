# urbansoccer_server/schemas/user_character_schema.py
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

class UserCharacterBase(BaseModel):
    """Schema base para personagens nomeados pelo usuário"""
    characterName: str = Field(..., min_length=1, max_length=50, description="Nome dado pelo usuário ao personagem")
    playerId: str = Field(..., description="ID do player (arquétipo) escolhido")
    userId: str = Field(..., description="ID do usuário que possui este personagem")

class UserCharacterCreate(BaseModel):
    """Schema para criação de novos personagens"""
    characterName: str = Field(..., min_length=1, max_length=50)
    playerId: str = Field(..., description="ID do player escolhido")

class UserCharacterUpdate(BaseModel):
    """Schema para atualização de personagens"""
    characterName: Optional[str] = Field(None, min_length=1, max_length=50)

class UserCharacterPublic(UserCharacterBase):
    """Schema público do personagem do usuário"""
    id: str = Field(..., alias="_id")
    createdAt: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={"ObjectId": str}
    )
    
    @classmethod
    def from_mongo(cls, character_dict: dict) -> "UserCharacterPublic":
        """Converte um documento do MongoDB para UserCharacterPublic"""
        if character_dict and "_id" in character_dict:
            character_dict["_id"] = str(character_dict["_id"])
        return cls(**character_dict)

class UserCharacterList(BaseModel):
    """Lista de personagens do usuário"""
    characters: List[UserCharacterPublic]

class UserCharacterWithPlayer(BaseModel):
    """Personagem do usuário com informações completas do player"""
    id: str = Field(..., alias="_id")
    characterName: str
    playerId: str
    userId: str
    createdAt: datetime
    
    # Informações do player (arquétipo)
    player: dict = Field(..., description="Dados completos do player escolhido")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={"ObjectId": str}
    )

class UserCharacterWithPlayerList(BaseModel):
    """Lista de personagens com informações dos players"""
    characters: List[UserCharacterWithPlayer]
