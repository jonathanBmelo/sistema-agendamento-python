from fastapi import FastAPI
from pydantic import BaseModel
from banco import cadastrar_usuario, buscar_usuario, buscar_servicos, salvar_agendamento

app = FastAPI(title="Sistema de Agendamento - Clínica de Estética")

import traceback
from fastapi import Request
from fastapi.responses import JSONResponse

app = FastAPI(title="Sistema de Agendamento - Clínica de Estética")

@app.exception_handler(Exception)
async def error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"erro": str(exc), "detalhe": traceback.format_exc()}
    )
# ─────────────────────────────────────────
# Modelos de entrada
# ─────────────────────────────────────────
class CadastroRequest(BaseModel):
    nome:    str
    celular: str
    email:   str
    senha:   str

class LoginRequest(BaseModel):
    email: str
    senha: str

class AgendamentoRequest(BaseModel):
    usuario_id:          int
    data:                str 
    horario:             str  
    servicos_escolhidos: list[int]
    total:               int

# ─────────────────────────────────────────
# Rotas
# ─────────────────────────────────────────
@app.get("/")
def inicio():
    return {"mensagem": "Sistema de Agendamento - Clínica de Estética"}

@app.post("/cadastro")
def cadastro(dados: CadastroRequest):
    sucesso = cadastrar_usuario(
        dados.nome,
        dados.celular,
        dados.email,
        dados.senha
    )
    if sucesso:
        return {"mensagem": f"Cadastro realizado com sucesso, {dados.nome}!"}
    else:
        return {"erro": "Este e-mail já está cadastrado."}

@app.post("/login")
def login(dados: LoginRequest):
    usuario = buscar_usuario(dados.email, dados.senha)
    if usuario:
        return {"mensagem": f"Bem-vindo, {usuario['nome']}!", "usuario": usuario}
    else:
        return {"erro": "E-mail ou senha inválidos."}

@app.get("/servicos")
def listar_servicos():
    servicos = buscar_servicos()
    lista = []
    for id, (nome, preco) in servicos.items():
        lista.append({"id": id, "nome": nome, "preco": preco})
    return {"servicos": lista}

@app.post("/agendamento")
def agendar(dados: AgendamentoRequest):
    sucesso = salvar_agendamento(
        usuario_id=dados.usuario_id,
        data=dados.data,
        horario=dados.horario,
        servicos_escolhidos=dados.servicos_escolhidos,
        total=dados.total
    )
    if sucesso:
        return {"mensagem": "Agendamento realizado com sucesso!"}
    else:
        return {"erro": "Erro ao realizar agendamento."}