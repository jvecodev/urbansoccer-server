# urbansoccer_server/main.py
from fastapi import FastAPI
from urbansoccer_server.api import players

app = FastAPI(
    title="Urban Soccer Server",
    description="Backend para o jogo Urban Soccer RPG.",
    version="0.1.0"
)

# Inclui o roteador de jogadores na aplicação principal
app.include_router(players.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Urban Soccer API"}