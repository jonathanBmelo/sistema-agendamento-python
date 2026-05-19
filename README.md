markdown# 💆 Sistema de Agendamento — Clínica de Estética

Sistema de agendamento interno para clínicas de estética, desenvolvido em Python com API REST, banco de dados PostgreSQL e interface web.

## ✨ Funcionalidades

- Login da atendente com senha criptografada
- Cadastro de clientes (nome, celular, e-mail)
- Edição e exclusão de clientes
- Busca de clientes por nome ou celular
- Catálogo de serviços com preços
- Agendamento de múltiplos serviços
- Campo de observações por agendamento
- Horário reduzido aos sábados (até 12h)
- Visualização da agenda do dia
- Cancelamento de agendamentos
- Dados salvos permanentemente no banco de dados

## 🛠️ Tecnologias utilizadas

- Python 3.14
- FastAPI + Uvicorn
- PostgreSQL 18
- psycopg2
- bcrypt
- python-dotenv
- HTML + CSS + JavaScript

## ⚙️ Como rodar o projeto

**1. Clone o repositório**
```bash
git clone https://github.com/jonathanBmelo/sistema-agendamento-python.git
```

**2. Instale as dependências**
```bash
pip install fastapi uvicorn psycopg2-binary bcrypt python-dotenv aiofiles
```

**3. Configure as variáveis de ambiente**

Crie um arquivo `.env` na raiz do projeto:
DB_HOST=localhost
DB_NAME=agendamento
DB_USER=postgres
DB_PASSWORD=sua_senha

**4. Inicialize o banco**
```bash
python banco.py
```

**5. Cadastre a atendente**
```python
from banco import cadastrar_atendente
cadastrar_atendente("Nome", "email@clinica.com", "senha123")
```

**6. Inicie o servidor**
```bash
python -m uvicorn main:app --reload
```

**7. Acesse o sistema**
http://localhost:8000/login-page

## 📁 Estrutura do projeto
sistema-agendamento-python/
│
├── banco.py          # conexão e operações com o banco de dados
├── main.py           # API FastAPI — rotas e lógica
├── .env              # credenciais (não versionado)
├── .gitignore
├── README.md
└── frontend/
├── login.html    # tela de login
├── index.html    # painel principal
├── style.css     # estilos
└── app.js        # lógica do front-end

## 🚀 Funcionalidades futuras

- [ ] Confirmação de agendamento via WhatsApp
- [ ] Histórico de agendamentos do cliente
- [ ] Docker
- [ ] Deploy em nuvem

## 👨‍💻 Autor

Jonathan Melo — [GitHub](https://github.com/jonathanBmelo)