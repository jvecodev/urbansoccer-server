# Estágio 1: Builder (Opcional, mas mantido para consistência)
FROM python:3.12-slim AS builder
WORKDIR /app

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Apenas para instalar o Poetry, se necessário em algum passo de CI/CD
RUN pip install poetry

# Estágio 2: Final
# Estágio 2: Final
FROM python:3.12-slim
WORKDIR /app

# Adicionamos 'requests' à lista
RUN pip install fastapi[standard] motor pydantic-settings python-jose[cryptography] passlib[bcrypt] python-multipart email-validator google-generativeai requests

# Copia o código da aplicação
COPY ./urbansoccer_server ./urbansoccer_server

EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "urbansoccer_server.main:app", "--host", "0.0.0.0", "--port", "8000"]