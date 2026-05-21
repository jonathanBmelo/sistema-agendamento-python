from auth import gerar_token, verificar_token
from fastapi import Depends
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
    buscar_horarios_ocupados,
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
        token = gerar_token({"id": atendente["id"], "email": atendente["email"]})
        return {"token": token, "atendente": atendente}
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
@app.get("/clientes")
def listar_clientes(token=Depends(verificar_token)):
    clientes = buscar_clientes()
    return {"clientes": clientes}

@app.post("/clientes")
def cadastrar(dados: ClienteRequest, token=Depends(verificar_token)):
    resultado = cadastrar_cliente(dados.nome, dados.celular, dados.email)
    if resultado["sucesso"]:
        return {"mensagem": "Cliente cadastrado com sucesso!", "cliente_id": resultado["cliente_id"]}
    else:
        return {"erro": resultado["erro"]}

@app.put("/clientes/{id}")
def editar(id: int, dados: EditarClienteRequest, token=Depends(verificar_token)):
    resultado = editar_cliente(id, dados.nome, dados.celular, dados.email)
    if resultado["sucesso"]:
        return {"mensagem": "Cliente atualizado com sucesso!"}
    else:
        return {"erro": resultado["erro"]}

@app.delete("/clientes/{id}")
def excluir(id: int, token=Depends(verificar_token)):
    resultado = excluir_cliente(id)
    if resultado["sucesso"]:
        return {"mensagem": "Cliente excluído com sucesso!"}
    else:
        return {"erro": resultado["erro"]}

@app.post("/agendamento")
def agendar(dados: AgendamentoRequest, token=Depends(verificar_token)):
    resultado = salvar_agendamento(
        cliente_id=dados.cliente_id,
        data=dados.data,
        horario=dados.horario,
        servicos_escolhidos=dados.servicos_escolhidos,
        total=dados.total,
        observacao=dados.observacao
    )
    if resultado["sucesso"]:
        return {"mensagem": "Agendamento realizado com sucesso!"}
    else:
        return {"erro": resultado["erro"]}

@app.delete("/agendamento/{id}")
def cancelar(id: int, token=Depends(verificar_token)):
    sucesso = cancelar_agendamento(id)
    if sucesso:
        return {"mensagem": "Agendamento cancelado com sucesso!"}
    else:
        return {"erro": "Erro ao cancelar agendamento."}

@app.get("/horarios-ocupados/{data}")
def horarios_ocupados(data: str, token=Depends(verificar_token)):
    ocupados = buscar_horarios_ocupados(data)
    return {"ocupados": ocupados}

@app.get("/agenda/{data}")
def agenda_do_dia(data: str, token=Depends(verificar_token)):
    agenda = buscar_agenda_do_dia(data)
    return {"data": data, "agendamentos": agenda}