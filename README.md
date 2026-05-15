# 💆 Sistema de Agendamento — Clínica de Estética

Sistema de agendamento online para clínicas de estética, desenvolvido em Python com integração a banco de dados PostgreSQL.

## ✨ Funcionalidades

- Cadastro e login de clientes com senha criptografada
- Catálogo de serviços com preços
- Agendamento de múltiplos serviços
- Escolha de data e horário disponíveis
- Horário reduzido aos sábados (até 12h)
- Dados salvos permanentemente no banco de dados

## 🛠️ Tecnologias utilizadas

- Python 3.14
- PostgreSQL 18
- psycopg2
- bcrypt

## 🚀 Funcionalidades futuras

- [ ] API REST com FastAPI
- [ ] Confirmação de agendamento via WhatsApp
- [ ] Histórico de agendamentos
- [ ] Cancelamento de consulta
- [ ] Área do administrador
- [ ] Interface web (Front-end)
- [ ] Docker
- [ ] Deploy em nuvem

## ⚙️ Como rodar o projeto

**1. Clone o repositório**
```bash
git clone https://github.com/jonathanBmelo/sistema-agendamento-estetica.git
```

**2. Instale as dependências**
```bash
pip install psycopg2-binary bcrypt
```

**3. Configure o banco de dados**

Crie um banco PostgreSQL chamado `agendamento` e configure as credenciais no arquivo `banco.py`.

**4. Inicialize o banco**
```bash
python banco.py
```

**5. Execute o sistema**
```bash
python agenda.py
```

## 📁 Estrutura do projeto
