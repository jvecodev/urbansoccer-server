# Estágio 1: Builder
FROM python:3.12-slim as builder
WORKDIR /app

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Instala o poetry e as dependências
RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev --no-root

# Estágio 2: Final
FROM python:3.12-slim
WORKDIR /app

# Copia as dependências instaladas do builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Copia o código da aplicação
COPY ./urbansoccer_server ./urbansoccer_server

EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "urbansoccer_server.main:app", "--host", "0.0.0.0", "--port", "8000"]