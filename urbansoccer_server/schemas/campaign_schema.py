# urbansoccer_server/schemas/campaign_schema.py
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

class CampaignProgress(BaseModel):
    level: int = Field(default=1, ge=1)
    score: int = Field(default=0, ge=0)
    currentMission: str = Field(default="Primeira Missão")
    inventory: List[str] = Field(default_factory=list)

class CampaignBase(BaseModel):
    userId: str = Field(..., description="ID do usuário proprietário da campanha")
    playerId: str = Field(..., description="ID do personagem escolhido")
    campaignName: Optional[str] = Field(None, max_length=100)
    status: str = Field(default="active", pattern=r"^(active|completed|abandoned)$")
    progress: CampaignProgress = Field(default_factory=CampaignProgress)

class CampaignCreate(BaseModel):
    playerId: str = Field(..., description="ID do personagem escolhido")
    campaignName: Optional[str] = Field(None, max_length=100)

class CampaignUpdate(BaseModel):
    campaignName: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[CampaignProgress] = None

class CampaignPublic(CampaignBase):
    id: str = Field(..., alias="_id")
    startDate: datetime
    lastPlayedDate: datetime

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
    """Campaign com detalhes do usuário e player"""
    user: Optional[dict] = None
    player: Optional[dict] = None

class CampaignList(BaseModel):
    campaigns: List[CampaignPublic]
