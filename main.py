import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

from banco import (
    cadastrar_cliente,
    buscar_clientes,
    editar_cliente,
    excluir_cliente,
    buscar_servicos,
    salvar_agendamento,
    cancelar_agendamento,
    buscar_agenda_do_dia,
    login_atendente
)

app = FastAPI(title="Sistema de Agendamento - Clínica de Estética")

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.exception_handler(Exception)
async def error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"erro": str(exc), "detalhe": traceback.format_exc()}
    )

# ─────────────────────────────────────────
# Modelos
# ─────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str
    senha: str

class ClienteRequest(BaseModel):
    nome:    str
    celular: str
    email:   Optional[str] = None

class EditarClienteRequest(BaseModel):
    nome:    str
    celular: str
    email:   Optional[str] = None

class AgendamentoRequest(BaseModel):
    cliente_id:          int
    data:                str
    horario:             str
    servicos_escolhidos: list[int]
    total:               int
    observacao:          Optional[str] = None
# ─────────────────────────────────────────
# Páginas
# ─────────────────────────────────────────
@app.get("/painel")
def painel():
    return FileResponse("frontend/index.html")

@app.get("/login-page")
def login_page():
    return FileResponse("frontend/login.html")

# ─────────────────────────────────────────
# Rotas públicas
# ─────────────────────────────────────────
@app.get("/")
def inicio():
    return {"mensagem": "Sistema de Agendamento - Clínica de Estética"}

@app.post("/login")
def login(dados: LoginRequest):
    atendente = login_atendente(dados.email, dados.senha)
    if atendente:
        return {"mensagem": f"Bem-vinda, {atendente['nome']}!", "atendente": atendente}
    else:
        return {"erro": "E-mail ou senha inválidos."}

@app.get("/servicos")
def listar_servicos():
    servicos = buscar_servicos()
    lista = []
    for id, (nome, preco) in servicos.items():
        lista.append({"id": id, "nome": nome, "preco": preco})
    return {"servicos": lista}

# ─────────────────────────────────────────
# Rotas de clientes
# ─────────────────────────────────────────
@app.post("/clientes")
def cadastrar(dados: ClienteRequest):
    resultado = cadastrar_cliente(dados.nome, dados.celular, dados.email)
    if resultado["sucesso"]:
        return {"mensagem": "Cliente cadastrado com sucesso!", "cliente_id": resultado["cliente_id"]}
    else:
        return {"erro": resultado["erro"]}

@app.get("/clientes")
def listar_clientes():
    clientes = buscar_clientes()
    return {"clientes": clientes}

@app.put("/clientes/{id}")
def editar(id: int, dados: EditarClienteRequest):
    resultado = editar_cliente(id, dados.nome, dados.celular, dados.email)
    if resultado["sucesso"]:
        return {"mensagem": "Cliente atualizado com sucesso!"}
    else:
        return {"erro": resultado["erro"]}

@app.delete("/clientes/{id}")
def excluir(id: int):
    resultado = excluir_cliente(id)
    if resultado["sucesso"]:
        return {"mensagem": "Cliente excluído com sucesso!"}
    else:
        return {"erro": resultado["erro"]}

# ─────────────────────────────────────────
# Rotas de agendamento
# ─────────────────────────────────────────
@app.post("/agendamento")
def agendar(dados: AgendamentoRequest):
    sucesso = salvar_agendamento(
        cliente_id=dados.cliente_id,
        data=dados.data,
        horario=dados.horario,
        servicos_escolhidos=dados.servicos_escolhidos,
        total=dados.total,
        observacao=dados.observacao
    )
    if sucesso:
        return {"mensagem": "Agendamento realizado com sucesso!"}
    else:
        return {"erro": "Erro ao realizar agendamento."}
    
@app.delete("/agendamento/{id}")
def cancelar(id: int):
    sucesso = cancelar_agendamento(id)
    if sucesso:
        return {"mensagem": "Agendamento cancelado com sucesso!"}
    else:
        return {"erro": "Erro ao cancelar agendamento."}

@app.get("/agenda/{data}")
def agenda_do_dia(data: str):
    agenda = buscar_agenda_do_dia(data)
    return {"data": data, "agendamentos": agenda}