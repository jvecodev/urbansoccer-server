# 🔧 Guia de Resolução dos Problemas

## **Problemas Identificados e Corrigidos:**

### 🐛 **Problema 1: Execução Local (Python) - Banco não funcionava**

**Causa:** Quando executava localmente com Python, não havia MongoDB disponível na porta 27017.

**Solução:** 
1. **Para desenvolvimento rápido:** Inicie um MongoDB local separado:
   ```bash
   docker run -d --name urbansoccer_mongo_dev -p 27017:27017 mongo:7
   ```

2. **Para parar quando não precisar:**
   ```bash
   docker stop urbansoccer_mongo_dev && docker rm urbansoccer_mongo_dev
   ```

### 🐳 **Problema 2: Docker Compose - API não iniciava na porta 8000**

**Causa:** Faltavam as dependências de autenticação no container Docker.

**Solução:** 
1. **Atualizei o `pyproject.toml`** com todas as dependências:
   ```toml
   python-jose = {extras = ["cryptography"], version = "^3.3.0"}
   passlib = {extras = ["bcrypt"], version = "^1.7.4"}
   python-multipart = "^0.0.9"
   email-validator = "^2.1.1"
   ```

2. **Simplifiquei o `Dockerfile`** para instalar via pip diretamente:
   ```dockerfile
   RUN pip install fastapi[standard] motor pydantic-settings python-jose[cryptography] passlib[bcrypt] python-multipart email-validator
   ```

3. **Adicionei variáveis de ambiente no `docker-compose.yaml`:**
   ```yaml
   environment:
     SECRET_KEY: Joao2006@
     ALGORITHM: HS256
     ACCESS_TOKEN_EXPIRE_MINUTES: 30
   ```

---

## **✅ Como Usar Agora:**

### **🏠 Desenvolvimento Local:**
```bash
# 1. Inicie o MongoDB local
docker run -d --name urbansoccer_mongo_dev -p 27017:27017 mongo:7

# 2. Execute a API localmente  
poetry shell
uvicorn urbansoccer_server.main:app --reload
```
- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs

### **🐳 Docker Compose (Produção/Completo):**
```bash
# Sobe API + MongoDB juntos
docker-compose up --build
```
- **API:** http://localhost:8000  
- **Docs:** http://localhost:8000/docs
- **MongoDB:** localhost:27018 (mapeado)

---

## **🔗 Endpoints Disponíveis:**

### **Autenticação:**
- `POST /users/register` - Registrar usuário
- `POST /users/login` - Login e obter token

### **Usuários (Requer Token):**
- `GET /users/me` - Perfil atual
- `GET /users/` - Listar usuários
- `GET /users/{id}` - Buscar por ID
- `PATCH /users/{id}` - Atualizar usuário
- `DELETE /users/{id}` - Deletar usuário

---

## **🔒 Segurança Implementada:**
- ✅ Senhas hasheadas com bcrypt
- ✅ Tokens JWT com expiração
- ✅ Validação de email único
- ✅ Rotas protegidas por autenticação
- ✅ Middleware de autenticação Bearer token

---

## **📱 Exemplo de Uso:**

1. **Registrar:**
   ```json
   POST /users/register
   {
     "name": "João Silva", 
     "email": "joao@test.com",
     "password": "senha123"
   }
   ```

2. **Login:**
   ```json
   POST /users/login
   {
     "email": "joao@test.com",
     "password": "senha123" 
   }
   ```

3. **Usar token nas rotas protegidas:**
   ```
   Authorization: Bearer {seu_token_aqui}
   ```

**🎉 Ambos os ambientes funcionando perfeitamente!**
