import psycopg2
import bcrypt
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

def conectar():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    return conn

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id       SERIAL PRIMARY KEY,
            nome     VARCHAR(100) NOT NULL,
            celular  VARCHAR(11)  NOT NULL,
            email    VARCHAR(100)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servicos (
            id    SERIAL PRIMARY KEY,
            nome  VARCHAR(100) NOT NULL,
            preco INTEGER      NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agendamentos (
            id          SERIAL PRIMARY KEY,
            cliente_id  INTEGER NOT NULL REFERENCES clientes(id),
            data        DATE    NOT NULL,
            horario     TIME    NOT NULL,
            total       INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agendamento_servicos (
            agendamento_id  INTEGER NOT NULL REFERENCES agendamentos(id),
            servico_id      INTEGER NOT NULL REFERENCES servicos(id),
            PRIMARY KEY (agendamento_id, servico_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS atendentes (
            id    SERIAL PRIMARY KEY,
            nome  VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            senha VARCHAR(100) NOT NULL
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Tabelas criadas com sucesso!")

def popular_servicos():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM servicos")
    quantidade = cursor.fetchone()[0]

    if quantidade > 0:
        cursor.close()
        conn.close()
        return

    lista_servicos = [
        ("Depilação com cera",                                40),
        ("Hidratação facial",                                 80),
        ("Limpeza de pele",                                   80),
        ("Massagem relaxante",                                80),
        ("Drenagem linfática corporal",                      100),
        ("Massagem modeladora",                              100),
        ("Tratamento de acne",                               120),
        ("Tratamento de estrias",                            150),
        ("Tratamentos faciais antirrugas / contra flacidez", 150),
        ("Peeling (químico ou diamante)",                    200),
    ]

    cursor.executemany("""
        INSERT INTO servicos (nome, preco)
        VALUES (%s, %s)
    """, lista_servicos)

    conn.commit()
    cursor.close()
    conn.close()
    print("Serviços cadastrados com sucesso!")

def cadastrar_cliente(nome, celular, email=None):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO clientes (nome, celular, email)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (nome, celular, email))

        cliente_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return {"sucesso": True, "cliente_id": cliente_id}

    except Exception as erro:
        conn.rollback()
        cursor.close()
        conn.close()
        return {"sucesso": False, "erro": str(erro)}

def buscar_clientes():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, celular, email
        FROM clientes
        ORDER BY nome
    """)

    resultados = cursor.fetchall()
    cursor.close()
    conn.close()

    clientes = []
    for id, nome, celular, email in resultados:
        clientes.append({"id": id, "nome": nome, "celular": celular, "email": email})

    return clientes

def buscar_servicos():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, preco
        FROM servicos
        ORDER BY id
    """)

    resultados = cursor.fetchall()
    cursor.close()
    conn.close()

    servicos = {}
    for id, nome, preco in resultados:
        servicos[id] = (nome, preco)

    return servicos

def salvar_agendamento(cliente_id, data, horario, servicos_escolhidos, total, observacao=None):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO agendamentos (cliente_id, data, horario, total, observacao)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (cliente_id, data, horario, total, observacao))

        agendamento_id = cursor.fetchone()[0]

        for servico_id in servicos_escolhidos:
            cursor.execute("""
                INSERT INTO agendamento_servicos (agendamento_id, servico_id)
                VALUES (%s, %s)
            """, (agendamento_id, servico_id))

        conn.commit()
        cursor.close()
        conn.close()
        return True

    except Exception as erro:
        conn.rollback()
        cursor.close()
        conn.close()
        print(f"Erro ao salvar agendamento: {erro}")
        return False

def cancelar_agendamento(agendamento_id):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM agendamento_servicos
            WHERE agendamento_id = %s
        """, (agendamento_id,))

        cursor.execute("""
            DELETE FROM agendamentos
            WHERE id = %s
        """, (agendamento_id,))

        conn.commit()
        cursor.close()
        conn.close()
        return True

    except Exception as erro:
        conn.rollback()
        cursor.close()
        conn.close()
        print(f"Erro ao cancelar agendamento: {erro}")
        return False
def buscar_agenda_do_dia(data):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            a.id,
            c.nome,
            c.celular,
            a.horario,
            a.total,
            a.observacao,
            STRING_AGG(s.nome, ', ' ORDER BY s.nome) AS servicos
        FROM agendamentos a
        JOIN clientes c ON c.id = a.cliente_id
        JOIN agendamento_servicos as_ ON as_.agendamento_id = a.id
        JOIN servicos s ON s.id = as_.servico_id
        WHERE a.data = %s
        GROUP BY a.id, c.nome, c.celular, a.horario, a.total, a.observacao
        ORDER BY a.horario
    """, (data,))

    resultados = cursor.fetchall()
    cursor.close()
    conn.close()

    agenda = []
    for id, nome, celular, horario, total, observacao, servicos in resultados:
        agenda.append({
            "id":         id,
            "nome":       nome,
            "celular":    celular,
            "horario":    str(horario),
            "total":      total,
            "observacao": observacao,
            "servicos":   servicos
        })

    return agenda

def login_atendente(email, senha):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, email, senha
        FROM atendentes
        WHERE email = %s
    """, (email,))

    atendente = cursor.fetchone()
    cursor.close()
    conn.close()

    if atendente is None:
        return None

    if not bcrypt.checkpw(senha.encode("utf-8"), atendente[3].encode("utf-8")):
        return None

    return {"id": atendente[0], "nome": atendente[1], "email": atendente[2]}

def cadastrar_atendente(nome, email, senha):
    conn = conectar()
    cursor = conn.cursor()

    try:
        senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())

        cursor.execute("""
            INSERT INTO atendentes (nome, email, senha)
            VALUES (%s, %s, %s)
        """, (nome, email, senha_hash.decode("utf-8")))

        conn.commit()
        cursor.close()
        conn.close()
        print("Atendente cadastrada com sucesso!")
        return True

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        cursor.close()
        conn.close()
        print("E-mail já cadastrado.")
        return False
    
def editar_cliente(cliente_id, nome, celular, email=None):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE clientes
            SET nome = %s, celular = %s, email = %s
            WHERE id = %s
        """, (nome, celular, email, cliente_id))

        conn.commit()
        cursor.close()
        conn.close()
        return {"sucesso": True}

    except Exception as erro:
        conn.rollback()
        cursor.close()
        conn.close()
        return {"sucesso": False, "erro": str(erro)}

def excluir_cliente(cliente_id):
    conn = conectar()
    cursor = conn.cursor()

    try:
        # Verifica se o cliente tem agendamentos
        cursor.execute("""
            SELECT COUNT(*) FROM agendamentos
            WHERE cliente_id = %s
        """, (cliente_id,))

        quantidade = cursor.fetchone()[0]

        if quantidade > 0:
            cursor.close()
            conn.close()
            return {"sucesso": False, "erro": f"Cliente possui {quantidade} agendamento(s) e não pode ser excluído."}

        cursor.execute("DELETE FROM clientes WHERE id = %s", (cliente_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return {"sucesso": True}

    except Exception as erro:
        conn.rollback()
        cursor.close()
        conn.close()
        return {"sucesso": False, "erro": str(erro)}


def editar_cliente(cliente_id, nome, celular, email=None):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE clientes
            SET nome = %s, celular = %s, email = %s
            WHERE id = %s
        """, (nome, celular, email, cliente_id))

        conn.commit()
        cursor.close()
        conn.close()
        return {"sucesso": True}

    except Exception as erro:
        conn.rollback()
        cursor.close()
        conn.close()
        return {"sucesso": False, "erro": str(erro)}

def excluir_cliente(cliente_id):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT COUNT(*) FROM agendamentos
            WHERE cliente_id = %s
        """, (cliente_id,))

        quantidade = cursor.fetchone()[0]

        if quantidade > 0:
            cursor.close()
            conn.close()
            return {"sucesso": False, "erro": f"Cliente possui {quantidade} agendamento(s) e não pode ser excluído."}

        cursor.execute("DELETE FROM clientes WHERE id = %s", (cliente_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return {"sucesso": True}

    except Exception as erro:
        conn.rollback()
        cursor.close()
        conn.close()
        return {"sucesso": False, "erro": str(erro)}
    

if __name__ == "__main__":
    criar_tabelas()
    popular_servicos()