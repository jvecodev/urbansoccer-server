# urbansoccer_server/api/users.py
from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from urbansoccer_server.models import user_model
from urbansoccer_server.schemas.user_schema import (
    UserCreate, 
    UserPublic, 
    UserList, 
    UserUpdate, 
    UserLogin, 
    Token
)
from urbansoccer_server.core.auth import create_access_token, get_current_user
from urbansoccer_server.core.config import settings

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserPublic)
async def register_user(user: UserCreate):
    """Registra um novo usuário"""
    # Verifica se o email já existe
    existing_user = await user_model.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email já está em uso"
        )
    
    user_dict = user.model_dump()
    created_user = await user_model.create_user(user_dict)
    return created_user

@router.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin):
    """Faz login do usuário e retorna token"""
    user = await user_model.authenticate_user(
        user_credentials.email, 
        user_credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserPublic)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Retorna o perfil do usuário atual"""
    return current_user

@router.get("/", status_code=status.HTTP_200_OK, response_model=UserList)
async def get_all_users(current_user: dict = Depends(get_current_user)):
    """Retorna todos os usuários (requer autenticação)"""
    users = await user_model.get_all_users()
    return {"users": users}

@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserPublic)
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Retorna um usuário específico"""
    user = await user_model.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Usuário não encontrado"
        )
    return user

@router.patch("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserPublic)
async def update_existing_user(
    user_id: str, 
    user_update: UserUpdate, 
    current_user: dict = Depends(get_current_user)
):
    """Atualiza dados do usuário"""
    update_data = user_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Nenhum dado para atualizar"
        )
        
    updated_user = await user_model.update_user(user_id, update_data)
    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Usuário não encontrado"
        )
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_user(
    user_id: str, 
    current_user: dict = Depends(get_current_user)
):
    """Deleta um usuário"""
    success = await user_model.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Usuário não encontrado"
        )
