# urbansoccer_server/models/user_model.py
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import List, Optional
from passlib.context import CryptContext

from urbansoccer_server.core.config import settings

# Configuração para hash de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Conexão com o banco
client = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.MONGO_DB]
user_collection = db["users"]

def hash_password(password: str) -> str:
    """Gera hash da senha"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha está correta"""
    return pwd_context.verify(plain_password, hashed_password)

async def create_user(user_data: dict) -> dict:
    """Cria um novo usuário com senha hasheada"""
    user_data["password"] = hash_password(user_data["password"])
    result = await user_collection.insert_one(user_data)
    new_user = await user_collection.find_one({"_id": result.inserted_id})
    # Remove a senha do retorno
    if new_user and "password" in new_user:
        del new_user["password"]
    return new_user

async def get_all_users() -> List[dict]:
    """Retorna todos os usuários sem as senhas"""
    users = await user_collection.find({}, {"password": 0}).to_list(length=None)
    return users

async def get_user_by_id(user_id: str) -> Optional[dict]:
    """Busca usuário por ID sem retornar a senha"""
    if not ObjectId.is_valid(user_id):
        return None
    user = await user_collection.find_one({"_id": ObjectId(user_id)}, {"password": 0})
    return user

async def get_user_by_email(email: str) -> Optional[dict]:
    """Busca usuário por email (incluindo senha para autenticação)"""
    return await user_collection.find_one({"email": email})

async def authenticate_user(email: str, password: str) -> Optional[dict]:
    """Autentica um usuário"""
    user = await get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user["password"]):
        return None
    # Remove a senha do retorno
    del user["password"]
    return user

async def update_user(user_id: str, data_to_update: dict) -> Optional[dict]:
    """Atualiza dados do usuário"""
    if not ObjectId.is_valid(user_id):
        return None
    
    # Se a senha está sendo atualizada, fazer o hash
    if "password" in data_to_update:
        data_to_update["password"] = hash_password(data_to_update["password"])
    
    await user_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": data_to_update}
    )
    return await get_user_by_id(user_id)

async def delete_user(user_id: str) -> bool:
    """Deleta um usuário"""
    if not ObjectId.is_valid(user_id):
        return False
    
    result = await user_collection.delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count > 0
