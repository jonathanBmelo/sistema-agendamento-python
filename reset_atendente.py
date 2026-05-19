from banco import cadastrar_atendente

# Primeiro apaga a atendente antiga
from banco import conectar
conn = conectar()
cursor = conn.cursor()
cursor.execute("DELETE FROM atendentes;")
conn.commit()
cursor.close()
conn.close()

# Cadastra novamente
cadastrar_atendente(
    nome="Atendente",
    email="atendente@clinica.com",
    senha="senha123"
)