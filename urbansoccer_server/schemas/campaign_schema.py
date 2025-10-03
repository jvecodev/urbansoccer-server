from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


class Card(BaseModel):
    actionId: str
    label: str
    description: str

class CampaignProgress(BaseModel):
    level: int = Field(default=1, ge=1)
    score: int = Field(default=0, ge=0)
    opponent_score: int = Field(default=0, ge=0)
    time: int = Field(default=0, description="Representa o 'lance' atual do jogo") 
    currentMission: str = Field(default="Primeira Missão")
    inventory: List[str] = Field(default_factory=list)
    availableCards: List[Card] = Field(default_factory=list) 
    gameContext: str = Field(default="meio_campo", description="Situação atual da partida") 

class CampaignBase(BaseModel):
    userId: str = Field(..., description="ID do usuário proprietário da campanha")
    userCharacterId: Optional[str] = Field(None, description="ID do personagem (user_character) escolhido para esta campanha")
    playerId: Optional[str] = Field(None, description="ID do player (campo antigo, para compatibilidade)")
    campaignName: str = Field(..., max_length=100)
    description: str = Field(...)
    status: str = Field(default="active", pattern=r"^(active|completed|abandoned)$")
    progress: CampaignProgress = Field(default_factory=CampaignProgress)

class CampaignCreate(BaseModel):
    userCharacterId: str = Field(..., description="ID do personagem (user_character) escolhido")
    campaignName: str = Field(..., max_length=100)
    description: str = Field(...)


class CampaignUpdate(BaseModel):
    """Schema para atualizações futuras na campanha."""
    campaignName: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[CampaignProgress] = None

class CampaignPublic(CampaignBase):
    """Schema público que será retornado pela API."""
    id: str = Field(..., alias="_id")
    startDate: datetime
    lastPlayedDate: Optional[datetime] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={"ObjectId": str}
    )
    
    @classmethod
    def from_mongo(cls, campaign_dict: dict) -> "CampaignPublic":
        """Converte um documento do MongoDB para CampaignPublic"""
        if campaign_dict and "_id" in campaign_dict:
            campaign_dict["_id"] = str(campaign_dict["_id"])
        return cls(**campaign_dict)

class CampaignWithDetails(CampaignPublic):
    """Campaign com detalhes do usuário e player."""
    user: Optional[dict] = None
    player: Optional[dict] = None

class CampaignList(BaseModel):
    campaigns: List[CampaignPublic]

class GameActionPayload(BaseModel):
    actionId: str = Field(..., description="O ID da ação que o jogador escolheu no card")


class GameState(BaseModel):
    score: str
    time: int 
    commentary: str
    gameContext: str = Field(default="meio_campo", description="A situação atual no campo") 

class PlayResponse(BaseModel):
    narration: str
    availableCards: List[Card]
    gameState: GameState