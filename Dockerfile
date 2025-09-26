# Estágio 1: Builder (Opcional, mas mantido para consistência)
FROM python:3.12-slim as builder
WORKDIR /app

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN pip install poetry

# Estágio 2: Final
FROM python:3.12-slim
WORKDIR /app

# Instalar dependências com versões específicas para resolver problemas de compatibilidade
RUN pip install fastapi[standard] motor pydantic-settings python-jose[cryptography] python-multipart email-validator google-generativeai requests elevenlabs bcrypt==4.0.1 passlib[bcrypt]==1.7.4 aiohttp google-generativeai

# Copia o código da aplicação
COPY ./urbansoccer_server ./urbansoccer_server

EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "urbansoccer_server.main:app", "--host", "0.0.0.0", "--port", "8000"]