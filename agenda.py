from banco import cadastrar_usuario, buscar_usuario, buscar_servicos, salvar_agendamento
from datetime import datetime, date, timedelta

# ─────────────────────────────────────────
# Funções
# ─────────────────────────────────────────
def gerar_horarios(sabado=False):
    horarios = []
    hora_atual = datetime.strptime("08:00", "%H:%M")
    hora_limite = datetime.strptime("11:30", "%H:%M") if sabado else datetime.strptime("17:30", "%H:%M")
    while hora_atual <= hora_limite:
        horarios.append(hora_atual.strftime("%H:%M"))
        hora_atual += timedelta(minutes=30)
    return horarios

def gerar_datas_validas():
    datas = []
    dia = date.today() + timedelta(days=1)
    while len(datas) < 30:
        if dia.weekday() != 6:
            datas.append(dia)
        dia += timedelta(days=1)
    return datas

DIAS_SEMANA = {
    0: "Segunda-feira",
    1: "Terça-feira",
    2: "Quarta-feira",
    3: "Quinta-feira",
    4: "Sexta-feira",
    5: "Sábado",
}

# ─────────────────────────────────────────
# Cabeçalho e menu
# ─────────────────────────────────────────
print("============= Agende sua consulta ====================")
print("Faça seu login ou cadastre-se")
print("1 - Login")
print("2 - Cadastro")

opcao = input("Escolha uma opção (1 ou 2): ")

autenticado   = False
usuario_logado = None  # ← guarda os dados do usuário logado

# ─────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────
if opcao == "1":
    email = input("Digite seu e-mail: ").strip()
    senha = input("Digite sua senha: ").strip()

    usuario_logado = buscar_usuario(email, senha)

    if usuario_logado:
        print(f"Login realizado com sucesso! Bem-vindo, {usuario_logado['nome']}!")
        autenticado = True
    else:
        print("E-mail ou senha inválidos.")

# ─────────────────────────────────────────
# CADASTRO
# ─────────────────────────────────────────
elif opcao == "2":
    nome    = input("Digite seu nome: ").strip()
    celular = input("Digite seu celular (com DDD): ").strip()
    email   = input("Digite seu e-mail: ").strip()
    senha   = input("Digite sua senha: ").strip()

    celular_limpo = celular.replace(" ", "").replace("-", "")

    if not nome.replace(" ", "").isalpha():
        print("Nome inválido. Use apenas letras.")
    elif not celular_limpo.isdigit() or len(celular_limpo) != 11:
        print("Celular inválido. Digite DDD + 9 dígitos (ex: 41991713860).")
    elif "@" not in email or "." not in email:
        print("E-mail inválido. O e-mail deve conter '@' e '.'")
    elif len(senha) < 6:
        print("Senha muito curta. Use no mínimo 6 caracteres.")
    else:
        sucesso = cadastrar_usuario(nome, celular_limpo, email, senha)
        if sucesso:
            usuario_logado = buscar_usuario(email, senha)
            autenticado = True

else:
    print("Opção inválida.")

# ─────────────────────────────────────────
# SERVIÇOS 
# ─────────────────────────────────────────
if autenticado:
    servicos = buscar_servicos()

    print("\n============= Serviços disponíveis =============")
    for numero, (nome, preco) in servicos.items():
        print(f"{numero:>2} - {nome:<45} R$ {preco}")
    print("=================================================")
    print("Digite 0 para finalizar a escolha.\n")

    servicos_escolhidos     = []  
    servicos_ids_escolhidos = []  
    while True:
        escolha = input("Escolha o número do serviço (0 para finalizar): ")

        if not escolha.isdigit():
            print("Entrada inválida. Digite apenas o número do serviço.")
            continue

        escolha = int(escolha)

        if escolha == 0:
            if not servicos_escolhidos:
                print("Nenhum serviço escolhido. Selecione ao menos um.")
                continue
            break

        if escolha not in servicos:
            print(f"Opção inválida. Escolha um número entre 1 e {len(servicos)}.")
            continue

        if any(s[0] == servicos[escolha][0] for s in servicos_escolhidos):
            print(f"'{servicos[escolha][0]}' já foi adicionado.")
            continue

        servicos_escolhidos.append(servicos[escolha])
        servicos_ids_escolhidos.append(escolha)  # ← guarda o id
        print(f"✔ '{servicos[escolha][0]}' adicionado!")

    # ─────────────────────────────────────────
    # DATA
    # ─────────────────────────────────────────
    DATAS_VALIDAS    = gerar_datas_validas()
    DATAS_POR_PAGINA = 7
    pagina           = 0

    print("\n============= Agendamento =============")

    while True:
        inicio        = pagina * DATAS_POR_PAGINA
        fim           = inicio + DATAS_POR_PAGINA
        datas_exibidas = DATAS_VALIDAS[inicio:fim]

        print(f"\n  Datas disponíveis (mostrando {inicio + 1}–{min(fim, len(DATAS_VALIDAS))} de {len(DATAS_VALIDAS)}):")
        print("  " + "─" * 40)
        for i, d in enumerate(datas_exibidas, start=inicio + 1):
            print(f"  {i:>2} - {d.strftime('%d/%m/%Y')} ({DIAS_SEMANA[d.weekday()]})")
        print("  " + "─" * 40)

        if fim < len(DATAS_VALIDAS):
            print("   M  - Ver mais datas")

        escolha_data = input("\n  Escolha o número da data desejada: ").strip().upper()

        if escolha_data == "M":
            if fim < len(DATAS_VALIDAS):
                pagina += 1
                continue
            else:
                print("  Não há mais datas disponíveis.")
                continue

        if not escolha_data.isdigit():
            print("  Entrada inválida. Digite o número da data ou M para ver mais.")
            continue

        escolha_data = int(escolha_data)

        if escolha_data < 1 or escolha_data > len(DATAS_VALIDAS):
            print(f"  Opção inválida. Escolha um número entre 1 e {len(DATAS_VALIDAS)}.")
            continue

        data_escolhida = DATAS_VALIDAS[escolha_data - 1]
        dia_semana     = DIAS_SEMANA[data_escolhida.weekday()]
        print(f"\n  ✔ Data escolhida: {data_escolhida.strftime('%d/%m/%Y')} — {dia_semana}")
        break

    # ─────────────────────────────────────────
    # HORÁRIO
    # ─────────────────────────────────────────
    HORARIOS_DISPONIVEIS = gerar_horarios(sabado=data_escolhida.weekday() == 5)

    print("\n  Horários disponíveis:")
    print("  " + "─" * 20)
    for i, horario in enumerate(HORARIOS_DISPONIVEIS, start=1):
        print(f"  {i:>2} - {horario}")
    print("  " + "─" * 20)

    while True:
        escolha_horario = input("\n  Escolha o número do horário desejado: ").strip()

        if not escolha_horario.isdigit():
            print("  Entrada inválida. Digite apenas o número do horário.")
            continue

        escolha_horario = int(escolha_horario)

        if escolha_horario < 1 or escolha_horario > len(HORARIOS_DISPONIVEIS):
            print(f"  Opção inválida. Escolha um número entre 1 e {len(HORARIOS_DISPONIVEIS)}.")
            continue

        horario_escolhido = HORARIOS_DISPONIVEIS[escolha_horario - 1]
        print(f"\n  ✔ Horário escolhido: {horario_escolhido}")
        break

    # ─────────────────────────────────────────
    # CONFIRMAÇÃO FINAL
    # ─────────────────────────────────────────
    total = sum(preco for _, preco in servicos_escolhidos)

    print("\n============= Confirmação do agendamento =============")
    print(f"  Nome:     {usuario_logado['nome']}")
    print(f"  Data:     {data_escolhida.strftime('%d/%m/%Y')} — {dia_semana}")
    print(f"  Horário:  {horario_escolhido}")
    print(f"\n  Serviços:")
    for nome, preco in servicos_escolhidos:
        print(f"    • {nome:<45} R$ {preco}")
    print(f"{'─' * 54}")
    print(f"  {'Total:':<49} R$ {total}")
    print("======================================================")

    # Salva no banco
    salvar_agendamento(
        usuario_id=usuario_logado['id'],
        data=data_escolhida,
        horario=horario_escolhido,
        servicos_escolhidos=servicos_ids_escolhidos,
        total=total
    )