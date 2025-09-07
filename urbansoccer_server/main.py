# urbansoccer_server/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from urbansoccer_server.api import users

app = FastAPI(
    title="Urban Soccer Server",
    description="Backend para o jogo Urban Soccer RPG com autenticação de usuários.",
    version="0.1.0"
)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui o roteador de usuários na aplicação principal
app.include_router(users.router, prefix="/users")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Urban Soccer API"}