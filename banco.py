import psycopg2
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

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
        CREATE TABLE IF NOT EXISTS usuarios (
            id       SERIAL PRIMARY KEY,
            nome     VARCHAR(100) NOT NULL,
            celular  VARCHAR(11)  NOT NULL,
            email    VARCHAR(100) NOT NULL UNIQUE,
            senha    VARCHAR(100) NOT NULL
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
            usuario_id  INTEGER NOT NULL REFERENCES usuarios(id),
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

def cadastrar_usuario(nome, celular, email, senha):
    conn = conectar()
    cursor = conn.cursor()

    try:
        senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())

        cursor.execute("""
            INSERT INTO usuarios (nome, celular, email, senha)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (nome, celular, email, senha_hash.decode("utf-8")))

        usuario_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Usuário cadastrado com sucesso! ID: {usuario_id}")
        return True

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        cursor.close()
        conn.close()
        print("Este e-mail já está cadastrado.")
        return False

def buscar_usuario(email, senha):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, email, senha
        FROM usuarios
        WHERE email = %s
    """, (email,))

    usuario = cursor.fetchone()
    cursor.close()
    conn.close()

    if usuario is None:
        return None

    # Compara a senha digitada com o hash salvo no banco
    if not bcrypt.checkpw(senha.encode("utf-8"), usuario[3].encode("utf-8")):
        return None

    return {
        "id":    usuario[0],
        "nome":  usuario[1],
        "email": usuario[2],
    }

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

def salvar_agendamento(usuario_id, data, horario, servicos_escolhidos, total):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO agendamentos (usuario_id, data, horario, total)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (usuario_id, data, horario, total))

        agendamento_id = cursor.fetchone()[0]

        for servico_id in servicos_escolhidos:
            cursor.execute("""
                INSERT INTO agendamento_servicos (agendamento_id, servico_id)
                VALUES (%s, %s)
            """, (agendamento_id, servico_id))

        conn.commit()
        cursor.close()
        conn.close()
        print("Agendamento salvo com sucesso!")
        return True

    except Exception as erro:
        conn.rollback()
        cursor.close()
        conn.close()
        print(f"Erro ao salvar agendamento: {erro}")
        return False

# ── Só executa ao rodar banco.py diretamente ──
if __name__ == "__main__":
    criar_tabelas()
    popular_servicos()