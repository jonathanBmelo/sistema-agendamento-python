# 💆 Sistema de Agendamento — Clínica de Estética

Sistema de agendamento interno para clínicas de estética, desenvolvido em Python com API REST, banco de dados PostgreSQL, autenticação JWT e interface web. Totalmente containerizado com Docker e deployado em produção.

🌐 **Demo:** [sistema-agendamento-python-production.up.railway.app](https://sistema-agendamento-python-production.up.railway.app/login-page)

## ✨ Funcionalidades

- Login da atendente com senha criptografada (bcrypt)
- Cadastro de clientes (nome, celular, e-mail)
- Edição e exclusão de clientes
- Busca de clientes por nome ou celular
- Catálogo de serviços com preços
- Agendamento de múltiplos serviços
- Campo de observações por agendamento
- Horários ocupados somem automaticamente da lista
- Horário reduzido aos sábados (até 12h)
- Visualização da agenda do dia
- Cancelamento de agendamentos
- Rotas protegidas por JWT
- Dados salvos permanentemente no banco de dados

## 🛠️ Tecnologias utilizadas

- Python 3.14
- FastAPI + Uvicorn
- PostgreSQL 18
- psycopg2
- bcrypt
- python-jose (JWT)
- python-dotenv
- HTML + CSS + JavaScript
- Docker + Docker Compose
- Railway (Deploy)

## 🐳 Como rodar com Docker

**1. Clone o repositório**
```bash
git clone https://github.com/jonathanBmelo/sistema-agendamento-python.git
cd sistema-agendamento-python
```

**2. Crie o arquivo `.env`**
DB_HOST=db
DB_NAME=agendamento
DB_USER=postgres
DB_PASSWORD=sua_senha
SECRET_KEY=sua_chave_secreta

**3. Suba os containers**
```bash
docker-compose up
```

**4. Inicialize o banco**
```bash
docker exec -it agendamento_app python -c "from banco import criar_tabelas, popular_servicos; criar_tabelas(); popular_servicos()"
```

**5. Cadastre a atendente**
```bash
docker exec -it agendamento_app python -c "from banco import cadastrar_atendente; cadastrar_atendente('Nome', 'email@clinica.com', 'senha')"
```

**6. Acesse o sistema**
http://localhost:8000/login-page

## ⚙️ Como rodar localmente (sem Docker)

**1. Instale as dependências**
```bash
pip install -r requirements.txt
```

**2. Crie o arquivo `.env`**

DB_HOST=localhost
DB_NAME=agendamento
DB_USER=postgres
DB_PASSWORD=sua_senha
SECRET_KEY=sua_chave_secreta

**3. Inicialize o banco**
```bash
python banco.py
```

**4. Inicie o servidor**
```bash
python -m uvicorn main:app --reload
```

**5. Acesse o sistema**

http://localhost:8000/login-page

## 📁 Estrutura do projeto

sistema-agendamento-python/
│
├── banco.py            # conexão e operações com o banco de dados
├── main.py             # API FastAPI — rotas e lógica
├── auth.py             # autenticação JWT
├── Dockerfile          # receita da imagem Docker
├── docker-compose.yml  # orquestra app + banco
├── requirements.txt    # dependências do projeto
├── .env                # credenciais (não versionado)
├── .gitignore
├── README.md
└── frontend/
├── login.html      # tela de login
├── index.html      # painel principal
├── style.css       # estilos
└── app.js          # lógica do front-end

## 🚀 Funcionalidades futuras

- [ ] Confirmação de agendamento via WhatsApp
- [ ] Histórico de agendamentos do cliente

## 👨‍💻 Autor

Jonathan Melo — [GitHub](https://github.com/jonathanBmelo) | [LinkedIn](https://www.linkedin.com/in/jonathan-melo)

