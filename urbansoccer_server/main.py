from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from urbansoccer_server.api import users, players, campaigns, user_character, narration, faq
from urbansoccer_server.core.database_init import initialize_database

app = FastAPI(
    title="Urban Soccer Server",
    description="Backend para o jogo Urban Soccer RPG com autenticação de usuários, personagens e campanhas.",
    version="0.2.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://urban-soccer.vercel.app",  
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "X-Conversation-ID"]
)
@app.on_event("startup")
async def startup_event():
    """Executa a inicialização do banco quando a aplicação inicia"""
    await initialize_database()

app.include_router(users.router)
app.include_router(players.router)
app.include_router(campaigns.router)
app.include_router(user_character.router)
app.include_router(narration.router)
app.include_router(faq.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Urban Soccer API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "urban-soccer-server"}