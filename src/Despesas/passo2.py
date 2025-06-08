import sys
import os
import csv

# Adiciona o diretório raiz do projeto ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.conexao_postgres import obter_conexao_postgres  # Função externa

# Caminho base relativo ao projeto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DESPESAS_PATH = os.path.join(BASE_DIR, "data", "despesas", "passo1")

# Gera anos com prefixo
anos_colunas = [f"ano_{ano}" for ano in range(1974, 2024)]

# Schemas por tipo
schemas = {
    "despesas_estado": [
        "nome", "fonte", "unidade", "tipo_unidade", "codigo_estado", "estado", *anos_colunas
    ],
    "despesas_municipio": [
        "nome", "fonte", "unidade", "tipo_unidade", "codigo_estado", "estado",
        "codigo_municipio", "municipio", *anos_colunas
    ],
}

def corrigir_csv_estrutura(caminho_entrada, caminho_saida, schema):
    with open(caminho_entrada, encoding="utf-8") as f_in:
        leitor = list(csv.reader(f_in))

    colunas_esperadas = len(schema)

    with open(caminho_saida, "w", newline='', encoding="utf-8") as f_out:
        escritor = csv.writer(f_out)
        escritor.writerow(schema)

        for linha in leitor[1:]:
            diff = colunas_esperadas - len(linha)
            if diff > 0:
                linha += [""] * diff
            elif diff < 0:
                linha = linha[:colunas_esperadas]
            escritor.writerow(linha)

def criar_tabela_se_nao_existir(cursor, tabela, colunas):
    colunas_sql = ', '.join(f'"{col}" TEXT' for col in colunas)
    cursor.execute(f'CREATE TABLE IF NOT EXISTS "{tabela}" ({colunas_sql});')

def inserir_csv_postgres(caminho_csv, tabela, colunas):
    conn = obter_conexao_postgres()
    cursor = conn.cursor()

    criar_tabela_se_nao_existir(cursor, tabela, colunas)

    with open(caminho_csv, encoding="utf-8") as f:
        leitor = csv.reader(f)
        next(leitor)  # pula cabeçalho

        placeholders = ','.join(['%s'] * len(colunas))
        cols = ','.join([f'"{col}"' for col in colunas])
        insert_sql = f'INSERT INTO "{tabela}" ({cols}) VALUES ({placeholders})'

        batch = []
        for linha in leitor:
            batch.append([None if val == "" else val for val in linha])
            if len(batch) >= 1000:
                cursor.executemany(insert_sql, batch)
                batch = []

        if batch:
            cursor.executemany(insert_sql, batch)

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Dados inseridos em {tabela}")

# Arquivos e tabelas
arquivos = [
    {
        "csv": os.path.join(DESPESAS_PATH, "despesa_estado.csv"),
        "tabela": "despesa_estado",
        "tipo": "despesas_estado"
    },
    {
        "csv": os.path.join(DESPESAS_PATH, "despesa_municipio.csv"),
        "tabela": "despesa_municipio",
        "tipo": "despesas_municipio"
    },
]

# Processamento
for item in arquivos:
    caminho = item["csv"]
    tabela = item["tabela"]
    tipo = item["tipo"]
    colunas = schemas[tipo]

    print(f"\n🔧 Corrigindo CSV: {caminho}")
    corrigir_csv_estrutura(caminho, caminho, colunas)

    print(f"📤 Inserindo dados em: {tabela}")
    try:
        inserir_csv_postgres(caminho, tabela, colunas)
    except Exception as e:
        print(f"❌ Erro ao inserir em {tabela}: {e}")
