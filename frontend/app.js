const API = "http://localhost:8000";

// Helper para enviar token em todas as requisições
function authHeaders() {
    const token = localStorage.getItem("token");
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
    };
}

// ─────────────────────────────────────────
// LOGIN
// ─────────────────────────────────────────
async function fazerLogin() {
    const email = document.getElementById("email").value;
    const senha = document.getElementById("senha").value;
    const erro  = document.getElementById("erro-login");

    const resposta = await fetch(`${API}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, senha })
    });

    const dados = await resposta.json();

    if (dados.erro) {
        erro.textContent = dados.erro;
        erro.style.display = "block";
        return;
    }

    localStorage.setItem("atendente", JSON.stringify(dados.atendente));
    localStorage.setItem("token", dados.token);
    window.location.href = "/painel";
}

// ─────────────────────────────────────────
// INICIALIZA O PAINEL
// ─────────────────────────────────────────
async function iniciarPainel() {
    const atendente = JSON.parse(localStorage.getItem("atendente"));

    if (!atendente) {
        window.location.href = "/login-page";
        return;
    }

    document.getElementById("nome-atendente").textContent = `Olá, ${atendente.nome}!`;

    const hoje = new Date().toISOString().split("T")[0];
    document.getElementById("data-agenda").value = hoje;
    document.getElementById("agendamento-data").value = hoje;

    await carregarClientes();
    await carregarServicos();
    await buscarAgenda();
    await gerarHorarios();
}

function sair() {
    localStorage.removeItem("atendente");
    localStorage.removeItem("token");
    window.location.href = "/login-page";
}

// ─────────────────────────────────────────
// AGENDA DO DIA
// ─────────────────────────────────────────
async function buscarAgenda() {
    const data  = document.getElementById("data-agenda").value;
    const corpo = document.getElementById("corpo-agenda");

    if (!data) return;

    const resposta = await fetch(`${API}/agenda/${data}`, {
        headers: authHeaders()
    });
    const dados = await resposta.json();

    if (dados.agendamentos.length === 0) {
        corpo.innerHTML = `<tr><td colspan="7" style="text-align:center; color:#aaa;">Nenhum agendamento para esta data</td></tr>`;
        return;
    }

    corpo.innerHTML = dados.agendamentos.map(a => `
        <tr>
            <td>${a.horario.substring(0, 5)}</td>
            <td>${a.nome}</td>
            <td>${a.celular}</td>
            <td>${a.servicos || '—'}</td>
            <td>${a.observacao || '—'}</td>
            <td>R$ ${a.total}</td>
            <td>
                <button 
                    class="secundario" 
                    style="width:auto; padding:6px 12px; font-size:12px; color:#c62828; background:#ffebee; border: 1px solid #ffcdd2;"
                    onclick="cancelarAgendamento(${a.id})">
                    Cancelar
                </button>
            </td>
        </tr>
    `).join("");
}

// ─────────────────────────────────────────
// CLIENTES
// ─────────────────────────────────────────
let todosClientes = [];

async function carregarClientes() {
    const resposta = await fetch(`${API}/clientes`, {
        headers: authHeaders()
    });
    const dados = await resposta.json();
    todosClientes = dados.clientes;
}

function filtrarClientes() {
    const busca     = document.getElementById("busca-cliente").value.toLowerCase().trim();
    const sugestoes = document.getElementById("sugestoes-clientes");
    const idHidden  = document.getElementById("agendamento-cliente");

    idHidden.value = "";

    if (busca.length < 1) {
        sugestoes.style.display = "none";
        return;
    }

    const filtrados = todosClientes.filter(c =>
        c.nome.toLowerCase().includes(busca) ||
        c.celular.includes(busca)
    );

    if (filtrados.length === 0) {
        sugestoes.innerHTML     = `<div class="sugestao-item" style="color:#aaa;">Nenhum cliente encontrado</div>`;
        sugestoes.style.display = "block";
        return;
    }

    sugestoes.innerHTML = filtrados.map(c => `
        <div class="sugestao-item" onclick="selecionarCliente(${c.id}, '${c.nome}', '${c.celular}')">
            ${c.nome} <span>${c.celular}</span>
        </div>
    `).join("");

    sugestoes.style.display = "block";
}

function selecionarCliente(id, nome, celular) {
    document.getElementById("busca-cliente").value       = `${nome} — ${celular}`;
    document.getElementById("agendamento-cliente").value = id;
    document.getElementById("sugestoes-clientes").style.display = "none";
}

async function cadastrarCliente() {
    const nome    = document.getElementById("cliente-nome").value.trim();
    const celular = document.getElementById("cliente-celular").value.trim();
    const email   = document.getElementById("cliente-email").value.trim();
    const erro    = document.getElementById("erro-cliente");
    const sucesso = document.getElementById("sucesso-cliente");

    erro.style.display    = "none";
    sucesso.style.display = "none";

    if (!nome || !celular) {
        erro.textContent   = "Nome e celular são obrigatórios.";
        erro.style.display = "block";
        return;
    }

    const resposta = await fetch(`${API}/clientes`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ nome, celular, email: email || null })
    });

    const dados = await resposta.json();

    if (dados.erro) {
        erro.textContent   = dados.erro;
        erro.style.display = "block";
        return;
    }

    sucesso.textContent   = `Cliente ${nome} cadastrado com sucesso!`;
    sucesso.style.display = "block";

    document.getElementById("cliente-nome").value    = "";
    document.getElementById("cliente-celular").value = "";
    document.getElementById("cliente-email").value   = "";

    await carregarClientes();
}

// ─────────────────────────────────────────
// SERVIÇOS
// ─────────────────────────────────────────
async function carregarServicos() {
    const resposta = await fetch(`${API}/servicos`, {
        headers: authHeaders()
    });
    const dados = await resposta.json();
    const lista = document.getElementById("lista-servicos");

    lista.innerHTML = dados.servicos.map(s => `
        <label class="servico-item">
            <input type="checkbox" value="${s.id}" data-preco="${s.preco}" onchange="calcularTotal()">
            ${s.nome} — R$ ${s.preco}
        </label>
    `).join("");
}

function calcularTotal() {
    const checkboxes = document.querySelectorAll("#lista-servicos input:checked");
    const total = Array.from(checkboxes).reduce((soma, cb) => soma + parseFloat(cb.dataset.preco), 0);
    document.getElementById("total-agendamento").textContent = `Total: R$ ${total.toFixed(2)}`;
}

// ─────────────────────────────────────────
// HORÁRIOS
// ─────────────────────────────────────────
async function gerarHorarios() {
    const select = document.getElementById("agendamento-horario");
    const data   = document.getElementById("agendamento-data").value;

    if (!data) return;

    const dia    = new Date(data + "T00:00:00").getDay();
    const fim    = dia === 6 ? "11:30" : "17:30";
    let hora     = new Date(`2000-01-01T08:00:00`);
    const limite = new Date(`2000-01-01T${fim}:00`);

    const resposta = await fetch(`${API}/horarios-ocupados/${data}`, {
        headers: authHeaders()
    });
    const dados    = await resposta.json();
    const ocupados = dados.ocupados;

    select.innerHTML = `<option value="">Selecione o horário</option>`;

    while (hora <= limite) {
        const h = hora.toTimeString().substring(0, 5);

        if (!ocupados.includes(h)) {
            select.innerHTML += `<option value="${h}">${h}</option>`;
        }

        hora = new Date(hora.getTime() + 30 * 60000);
    }
}

// ─────────────────────────────────────────
// AGENDAMENTO
// ─────────────────────────────────────────
async function realizarAgendamento() {
    const cliente_id = parseInt(document.getElementById("agendamento-cliente").value);
    const data       = document.getElementById("agendamento-data").value;
    const horario    = document.getElementById("agendamento-horario").value;
    const observacao = document.getElementById("agendamento-observacao").value.trim();
    const erro       = document.getElementById("erro-agendamento");
    const sucesso    = document.getElementById("sucesso-agendamento");

    erro.style.display    = "none";
    sucesso.style.display = "none";

    const checkboxes = document.querySelectorAll("#lista-servicos input:checked");
    const servicos   = Array.from(checkboxes).map(cb => parseInt(cb.value));
    const total      = Array.from(checkboxes).reduce((soma, cb) => soma + parseFloat(cb.dataset.preco), 0);

    if (!cliente_id || !data || !horario || servicos.length === 0) {
        erro.textContent   = "Preencha todos os campos e selecione ao menos um serviço.";
        erro.style.display = "block";
        return;
    }

    const resposta = await fetch(`${API}/agendamento`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ cliente_id, data, horario, servicos_escolhidos: servicos, total, observacao: observacao || null })
    });

    const dados = await resposta.json();

    if (dados.erro) {
        erro.textContent   = dados.erro;
        erro.style.display = "block";
        return;
    }

    sucesso.textContent   = "Agendamento realizado com sucesso!";
    sucesso.style.display = "block";

    document.getElementById("data-agenda").value = data;
    document.getElementById("agendamento-observacao").value = "";
    await buscarAgenda();
    await gerarHorarios();

    checkboxes.forEach(cb => cb.checked = false);
    calcularTotal();
}

// ─────────────────────────────────────────
// CANCELAR AGENDAMENTO
// ─────────────────────────────────────────
async function cancelarAgendamento(id) {
    if (!confirm("Tem certeza que deseja cancelar este agendamento?")) return;

    const resposta = await fetch(`${API}/agendamento/${id}`, {
        method: "DELETE",
        headers: authHeaders()
    });

    const dados = await resposta.json();

    if (dados.erro) {
        alert(dados.erro);
        return;
    }

    alert("Agendamento cancelado com sucesso!");
    await buscarAgenda();
    await gerarHorarios();
}

// ─────────────────────────────────────────
// LISTA DE CLIENTES
// ─────────────────────────────────────────
function renderizarListaClientes(clientes) {
    const corpo = document.getElementById("corpo-clientes");

    if (clientes.length === 0) {
        corpo.innerHTML = `<tr><td colspan="4" style="text-align:center; color:#aaa;">Nenhum cliente encontrado</td></tr>`;
        return;
    }

    corpo.innerHTML = clientes.map(c => `
        <tr>
            <td>${c.nome}</td>
            <td>${c.celular}</td>
            <td>${c.email || '—'}</td>
            <td style="display:flex; gap:6px;">
                <button 
                    style="width:auto; padding:6px 12px; font-size:12px;"
                    onclick="abrirModal(${c.id}, '${c.nome}', '${c.celular}', '${c.email || ''}')">
                    ✏️ Editar
                </button>
                <button 
                    class="secundario"
                    style="width:auto; padding:6px 12px; font-size:12px; color:#c62828; background:#ffebee; border:1px solid #ffcdd2;"
                    onclick="excluirCliente(${c.id}, '${c.nome}')">
                    🗑️ Excluir
                </button>
            </td>
        </tr>
    `).join("");
}

function filtrarListaClientes() {
    const busca  = document.getElementById("filtro-lista-clientes").value.toLowerCase().trim();
    const tabela = document.getElementById("tabela-clientes");

    if (busca.length < 1) {
        tabela.style.display = "none";
        return;
    }

    const filtrados = todosClientes.filter(c =>
        c.nome.toLowerCase().includes(busca) ||
        c.celular.includes(busca)
    );

    tabela.style.display = "table";
    renderizarListaClientes(filtrados);
}

// ─────────────────────────────────────────
// EDITAR CLIENTE
// ─────────────────────────────────────────
function abrirModal(id, nome, celular, email) {
    document.getElementById("editar-id").value      = id;
    document.getElementById("editar-nome").value    = nome;
    document.getElementById("editar-celular").value = celular;
    document.getElementById("editar-email").value   = email;
    document.getElementById("modal-editar").style.display = "block";
}

function fecharModal() {
    document.getElementById("modal-editar").style.display = "none";
}

async function salvarEdicao() {
    const id      = document.getElementById("editar-id").value;
    const nome    = document.getElementById("editar-nome").value.trim();
    const celular = document.getElementById("editar-celular").value.trim();
    const email   = document.getElementById("editar-email").value.trim();

    const resposta = await fetch(`${API}/clientes/${id}`, {
        method: "PUT",
        headers: authHeaders(),
        body: JSON.stringify({ nome, celular, email: email || null })
    });

    const dados = await resposta.json();

    if (dados.erro) {
        alert(dados.erro);
        return;
    }

    alert("Cliente atualizado com sucesso!");
    fecharModal();
    await carregarClientes();
    renderizarListaClientes(todosClientes);
}

// ─────────────────────────────────────────
// EXCLUIR CLIENTE
// ─────────────────────────────────────────
async function excluirCliente(id, nome) {
    if (!confirm(`Tem certeza que deseja excluir o cliente "${nome}"?`)) return;

    const resposta = await fetch(`${API}/clientes/${id}`, {
        method: "DELETE",
        headers: authHeaders()
    });

    const dados = await resposta.json();

    if (dados.erro) {
        alert(dados.erro);
        return;
    }

    alert("Cliente excluído com sucesso!");
    await carregarClientes();
    renderizarListaClientes(todosClientes);
}

// ─────────────────────────────────────────
// INICIA O PAINEL SE ESTIVER NA PÁGINA CERTA
// ─────────────────────────────────────────
if (document.getElementById("nome-atendente")) {
    iniciarPainel();
}

const inputData = document.getElementById("agendamento-data");
if (inputData) {
    inputData.addEventListener("change", gerarHorarios);
}