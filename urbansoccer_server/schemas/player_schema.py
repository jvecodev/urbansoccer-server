# urbansoccer_server/schemas/player_schema.py
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

class PlayerStats(BaseModel):
    speed: int = Field(..., ge=1, le=200)
    attack: int = Field(..., ge=1, le=200)
    defense: int = Field(..., ge=1, le=200)
    leadership: int = Field(..., ge=1, le=200)
    specialAbility: str

class PlayerBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: str = Field(..., min_length=10, max_length=500)
    rarity: str = Field(..., pattern=r"^(default|unique)$")
    stats: PlayerStats
    imageUrl: str = Field(..., description="URL da imagem do personagem")
    isAvailable: bool = True

class PlayerCreate(PlayerBase):
    pass

class PlayerUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    rarity: Optional[str] = None
    stats: Optional[PlayerStats] = None
    imageUrl: Optional[str] = None
    isAvailable: Optional[bool] = None

class PlayerPublic(PlayerBase):
    id: str = Field(..., alias="_id")
    createdAt: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={"ObjectId": str}
    )
    
    @classmethod
    def from_mongo(cls, player_dict: dict) -> "PlayerPublic":
        """Converte um documento do MongoDB para PlayerPublic"""
        if player_dict and "_id" in player_dict:
            player_dict["_id"] = str(player_dict["_id"])
        return cls(**player_dict)

class PlayerList(BaseModel):
    players: List[PlayerPublic]