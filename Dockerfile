# Estágio 1: Builder
FROM python:3.12-slim as builder
WORKDIR /app

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Instala o poetry e as dependências principais via pip (temporário)
RUN pip install poetry
RUN pip install fastapi[standard] motor pydantic-settings python-jose[cryptography] passlib[bcrypt] python-multipart email-validator

# Estágio 2: Final
FROM python:3.12-slim
WORKDIR /app

# Instala as dependências via pip diretamente
RUN pip install fastapi[standard] motor pydantic-settings python-jose[cryptography] passlib[bcrypt] python-multipart email-validator

# Copia o código da aplicação
COPY ./urbansoccer_server ./urbansoccer_server

EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "urbansoccer_server.main:app", "--host", "0.0.0.0", "--port", "8000"]