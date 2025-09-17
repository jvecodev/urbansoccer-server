# Urban Soccer Server 🏈

Backend para o jogo Urban Soccer RPG com sistema completo de usuários, personagens únicos e campanhas.

## 🚀 Quick Start com Docker

### Pré-requisitos
- Docker
- Docker Compose

### Setup Completo (1 comando)

```bash
# Primeira vez
./docker-setup.sh setup
```

Isso irá:
1. ✅ Construir e iniciar API + MongoDB
2. ✅ Criar os 5 personagens padrão
3. ✅ Mostrar status dos serviços

### Comandos Disponíveis

```bash
# Setup completo na primeira vez
./docker-setup.sh setup

# Iniciar serviços
./docker-setup.sh start

# Parar serviços
./docker-setup.sh stop

# Reiniciar serviços
./docker-setup.sh restart

# Ver status
./docker-setup.sh status

# Ver logs em tempo real
./docker-setup.sh logs

# Popular personagens (se ainda não foi feito)
./docker-setup.sh populate

# Reset completo (CUIDADO: apaga tudo!)
./docker-setup.sh reset
```

### Acessos

- **API**: http://localhost:8000
- **Documentação Interativa**: http://localhost:8000/docs
- **MongoDB**: localhost:27017

## 📂 Estrutura de Arquivos
```bash
urbansoccer-server/
├── urbansoccer_server/
│   ├── api/
│   │   └── players.py        # Controller: Endpoints de jogadores
│   ├── core/
│   │   └── config.py         # Configurações centrais
│   ├── models/
│   │   └── player_model.py   # Model: Lógica de banco de dados
│   ├── schemas/
│   │   └── player_schema.py  # Schema (View): Modelos Pydantic
│   └── main.py                 # Ponto de entrada da aplicação
│
├── .gitignore                # Arquivos ignorados pelo Git
├── Dockerfile                # Receita para a imagem Docker da API
├── docker-compose.yaml       # Orquestrador dos serviços (API + DB)
├── pyproject.toml            # Definições e dependências do projeto (Poetry)
└── poetry.lock               # Arquivo de lock para dependências consistentes
```

---

## 🚀 Tecnologias Principais
- **FastAPI**: Framework web moderno para construção de APIs em Python.
- **MongoDB**: Banco de dados NoSQL orientado a documentos, ideal para flexibilidade e escalabilidade.
- **AsyncMongoClient**: Driver assíncrono oficial para usar MongoDB com pymongo.
- **Pydantic**: Para validação de dados e gerenciamento de configurações.
- **Poetry**: Gerenciamento de dependências e ambientes virtuais.
- **Docker & Docker Compose**: Para criar um ambiente containerizado, consistente e isolado.

---

## 🛠️ Como Executar o Projeto
Existem duas maneiras de executar o servidor:  
**localmente com Poetry** ou **containerizado com Docker (recomendado).**

### ✅ Pré-requisitos
- Python **3.12+**
- Poetry (para execução local)
- Docker e Docker Compose (para execução em container)

---

### 🔹 Opção 1: Execução com Docker (Recomendado)
Este método sobe tanto a API quanto o banco de dados MongoDB, já conectados, com um único comando.

1. Clone o repositório:
   ```bash
   git clone <https://github.com/jvecodev/urbansoccer-server>
   cd urbansoccer-server
   ```

2. Rode o comando:
     ```bash
    docker-compose up --build
    ```
  ###  O Docker irá construir a imagem da API e baixar a imagem do MongoDB.

  ### Os serviços serão iniciados e a API se conectará automaticamente ao banco.

  * API disponível em: http://localhost:8000

  * Documentação interativa (Swagger UI): http://localhost:8000/docs

### Opção 2: Execução Local (com Poetry)
Este método é útil para desenvolvimento rápido, mas requer que você tenha uma instância do MongoDB rodando separadamente.

1. rode o comando
   ```bash
    poetry install
   ```
2. Ative o ambiente virtual
   ```bash
   poetry shell
   ```
3. Inicie o servidor de desenvolvimento
   ```bash
   uvicorn urbansoccer_server.main:app --reload
   ```

##📄 Endpoints da API
### A API atualmente expõe os seguintes endpoints sob o prefixo /players:
* POST /players/: Cria um novo jogador.

* GET /players/: Lista todos os jogadores.

* GET /players/{player_id}: Busca um jogador específico pelo seu ID.

* PATCH /players/{player_id}: Atualiza as informações de um jogador.

* DELETE /players/{player_id}: Remove um jogador do banco de dados.

###Todos o endpoints podem ser testados:
```bash
http://localhost:8000/docs.
```
