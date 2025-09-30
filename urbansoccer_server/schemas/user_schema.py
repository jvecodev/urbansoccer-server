# urbansoccer_server/schemas/user_schema.py
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional, Any
from bson import ObjectId

class UserBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)

class UserUpdate(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None

class UserPublic(UserBase):
    id: str = Field(..., alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    @classmethod
    def from_mongo(cls, user_dict: dict) -> "UserPublic":
        """Converte um documento do MongoDB para UserPublic"""
        if user_dict and "_id" in user_dict:
            user_dict["_id"] = str(user_dict["_id"])
        return cls(**user_dict)

class UserList(BaseModel):
    users: List[UserPublic]

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
