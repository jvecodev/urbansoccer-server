
# Urban Soccer: Backend API

## 📖 Sobre o Projeto

Este repositório contém o **código-fonte do backend** para o projeto **Urban Soccer**, um RPG de ação textual imersivo, onde cada partida é uma história única, narrada e moldada por Inteligência Artificial.

Construído com **FastAPI** e projetado para ser robusto e escalável, este servidor é o cérebro por trás da experiência do jogador, gerenciando a lógica do jogo, a persistência de dados e a integração com múltiplos provedores de Large Language Models (LLMs) para gerar narrativas dinâmicas.

---

## 🚀 Tecnologias Utilizadas

A API é construída utilizando uma stack moderna de Python, focada em performance, modularidade e boas práticas de desenvolvimento.

-   **Framework Principal**:
    -   **FastAPI**: Para a construção de APIs assíncronas de alta performance.
    -   **Uvicorn**: Como o servidor ASGI que executa a aplicação.

-   **Banco de Dados**:
    -   **MongoDB**: Banco de dados NoSQL orientado a documentos.
    -   **Beanie**: Um ODM (Object-Document Mapper) assíncrono para MongoDB, construído sobre Pydantic e Motor.

-   **Gerenciamento de Dependências**:
    -   **Poetry**: Para um gerenciamento de pacotes, dependências e ambientes virtuais de forma robusta e determinística.

-   **Validação e Schemas**:
    -   **Pydantic**: Para validação de dados, serialização e documentação automática de schemas.

-   **Autenticação e Segurança**:
    -   **JWT (JSON Web Tokens)**: Para proteger os endpoints e gerenciar as sessões dos usuários.
    -   **Passlib & bcrypt**: Para hashing seguro de senhas.
    -   **python-jose**: Para codificar, decodificar e assinar tokens JWT.

-   **Inteligência Artificial e LLMs**:
    -   **Abstração**: Criei minha própria camada de abstração para utilizar as demais Inteligencias, no arquivo llm_provider.
    -   **Google AI Studio**: Integrado para usar os modelos da família **Gemini** (ex: `gemini-2.5-flash`).
    -   **Groq**: Para acesso a modelos de alta velocidade, como o **Llama 3** (`llama3-70b-8192`).
    -   **Cerebras**: Para acesso aos modelos **Llama 3.1** (`llama3.1-8b`, `llama3.1-70b`).
    -   **ElevenLabs**: Para a funcionalidade de Text-to-Speech (TTS), convertendo as narrações do jogo em áudio de alta qualidade.

-   **Containerização**:
    -   **Docker** e **Docker Compose**: Para criar um ambiente de desenvolvimento e produção consistente, incluindo a API e o banco de dados.

---

## 🛠️ Como Executar o Projeto

Existem duas maneiras principais de executar o backend: **localmente com Poetry** ou via **Docker** (recomendado para simplicidade).

### 🔹 Pré-requisitos

-   **Python** (versão 3.10 ou superior)
-   **Poetry** (gerenciador de dependências)
-   **Docker** e **Docker Compose** (para a execução com container)
-   Um arquivo `.env` (você pode copiar o `.env.example`)
-   Chaves de API para os serviços de IA (Google AI Studio, Groq, Cerebras, ElevenLabs).

### 1. Execução com Docker (Recomendado)

Este é o método mais simples e rápido para colocar o ambiente para rodar, pois já inclui o banco de dados.

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/jvecodev/urbansoccer-server.git](https://github.com/jvecodev/urbansoccer-server.git)
    cd urbansoccer-server
    ```

2.  **Configure as Variáveis de Ambiente:**
    Copie o arquivo de exemplo `.env.example` para um novo arquivo chamado `.env`.
    ```bash
    cp .env.example .env
    ```
    Abra o arquivo `.env` e preencha com suas chaves de API: `GOOGLE_AISTUDIO_KEY`, `GROQ_KEY`, `CEREBRAS_KEY`, e `ELEVENLABS_API_KEY`. As configurações de banco de dados no `docker-compose.yaml` já estão alinhadas com os valores padrão.

3.  **Construa e inicie os containers:**
    Este comando irá construir a imagem da API e iniciar o container do MongoDB.
    ```bash
    docker-compose up --build
    ```

4.  **Acesse a API:**
    A API estará disponível em `http://localhost:8000`. A documentação interativa (Swagger UI) pode ser acessada em `http://localhost:8000/docs`.

### 2. Execução Local com Poetry

Este método requer que você tenha uma instância do MongoDB rodando separadamente.

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/jvecodev/urbansoccer-server.git](https://github.com/jvecodev/urbansoccer-server.git)
    cd urbansoccer-server
    ```

2.  **Instale as dependências:**
    O Poetry criará um ambiente virtual e instalará todas as dependências.
    ```bash
    poetry install
    ```

3.  **Configure as Variáveis de Ambiente:**
    Copie o `.env.example` para `.env` e preencha as variáveis, incluindo as chaves de API. Certifique-se de que a `MONGO_URI` aponta para a sua instância do MongoDB.
    ```bash
    cp .env.example .env
    ```

4.  **Inicie o servidor de desenvolvimento:**
    Execute o servidor Uvicorn através do Poetry. O Uvicorn irá recarregar automaticamente a aplicação a cada alteração no código.
    ```bash
    poetry run uvicorn urbansoccer_server.main:app --host 0.0.0.0 --port 8000 --reload
    ```

5.  **Acesse a API:**
    Acesse `http://localhost:8000/docs` para interagir com a documentação da API.

---

## 🏗️ Estrutura do Projeto

O projeto segue uma estrutura modular e organizada para facilitar a manutenção e escalabilidade.

```bash
urbansoccer-server/
├── urbansoccer_server/
│   ├── api/                 # Módulos de Rota (Endpoints da API)
│   │   ├── campaigns.py
│   │   ├── faq.py
│   │   ├── narration.py
│   │   ├── players.py
│   │   ├── user_character.py
│   │   └── users.py
│   ├── assets/              # Imagens e outros assets estáticos
│   ├── core/                # Configurações centrais e lógica de núcleo
│   │   ├── auth.py          # Lógica de autenticação e JWT
│   │   ├── config.py        # Carregamento de variáveis de ambiente
│   │   └── database_init.py # Inicialização do banco de dados e dados iniciais
│   ├── models/              # Definições de modelos de dados (Beanie ODM)
│   │   ├── campaign_model.py
│   │   └── user_model.py    # ... e outros
│   ├── schemas/             # Schemas Pydantic (validação de dados)
│   │   ├── campaign_schema.py
│   │   └── user_schema.py   # ... e outros
│   ├── services/            # Lógica de negócio e integrações
│   │   ├── campaign_generator.py # Serviço para gerar campanhas com IA
│   │   ├── game_logic.py       # Lógica principal do jogo
│   │   ├── game_narrator.py    # Serviço de narração com IA
│   │   ├── llm_provider.py     # Abstração para os provedores de LLM
│   │   ├── prompt_templates.py # Templates de prompts para os LLMs
│   │   └── tts_service.py      # Serviço de Text-to-Speech
│   └── main.py              # Ponto de entrada da aplicação FastAPI
├── .env.example             # Exemplo de arquivo de variáveis de ambiente
├── docker-compose.yaml      # Configuração do Docker Compose
├── Dockerfile               # Instruções para construir a imagem Docker da API
├── poetry.lock              # Arquivo de lock de dependências
└── pyproject.toml           # Definição de dependências e metadados do projeto
```
