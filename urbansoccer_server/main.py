# urbansoccer_server/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from urbansoccer_server.api import users, players, campaigns, user_character
from urbansoccer_server.core.database_init import initialize_database

app = FastAPI(
    title="Urban Soccer Server",
    description="Backend para o jogo Urban Soccer RPG com autenticação de usuários, personagens e campanhas.",
    version="0.2.0"
)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Evento de inicialização
@app.on_event("startup")
async def startup_event():
    """Executa a inicialização do banco quando a aplicação inicia"""
    await initialize_database()

# Inclui os roteadores na aplicação principal
app.include_router(users.router, prefix="/users")
app.include_router(players.router)
app.include_router(campaigns.router)
app.include_router(user_character.router, prefix="/characters")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Urban Soccer API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "urban-soccer-server"}