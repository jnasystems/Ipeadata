import csv
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.conexao_postgres import obter_conexao_postgres  # função de conexão

# Gera anos com prefixo
anos_colunas = [f"ano_{ano}" for ano in range(1974, 2025)]

# Schemas organizados por tipo
schemas = {
    "brasil": [
        "nome", "fonte", "unidade", "codigo_brasil", "brasil", *anos_colunas
    ],
    "regioes": [
        "nome", "fonte", "unidade", "codigo_brasil", "brasil", "codigo_regiao", "regiao", *anos_colunas
    ],
    "estados": [
        "nome", "fonte", "unidade", "codigo_brasil", "brasil", "codigo_regiao", "regiao", "codigo_estado", "estado", *anos_colunas
    ],
    "mesorregioes": [
        "nome", "fonte", "unidade", "codigo_brasil", "brasil", "codigo_regiao", "regiao",
        "codigo_estado", "estado", "codigo_mesorregiao", "mesorregiao", *anos_colunas
    ],
    "microrregioes": [
        "nome", "fonte", "unidade", "codigo_brasil", "brasil", "codigo_regiao", "regiao",
        "codigo_estado", "estado", "codigo_mesorregiao", "mesorregiao",
        "codigo_microrregiao", "microrregiao", *anos_colunas
    ],
    "municipio": [
        "nome", "fonte", "unidade", "codigo_brasil", "brasil", "codigo_regiao", "regiao",
        "codigo_estado", "estado", "codigo_mesorregiao", "mesorregiao",
        "codigo_microrregiao", "microrregiao", "codigo_municipio", "municipio", *anos_colunas
    ],
}

# Corrigir CSV para ter o número certo de colunas
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

# Cria a tabela no banco, se não existir
def criar_tabela_se_nao_existir(cursor, tabela, colunas):
    colunas_sql = ', '.join(f'"{col}" TEXT' for col in colunas)
    cursor.execute(f'CREATE TABLE IF NOT EXISTS "{tabela}" ({colunas_sql});')

# Insere o CSV no banco
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
arquivos_e_tabelas = [
    {"csv": "data/area colhida/passo1/area_colhida_municipios.csv",     "tabela": "area_colhida_municipios",      "tipo": "municipio"},
    {"csv": "data/area colhida/passo2/area_colhida_brasil.csv",         "tabela": "area_colhida_brasil",          "tipo": "brasil"},
    {"csv": "data/area colhida/passo2/area_colhida_regiao.csv",         "tabela": "area_colhida_regioes",         "tipo": "regioes"},
    {"csv": "data/area colhida/passo2/area_colhida_estado.csv",         "tabela": "area_colhida_estados",         "tipo": "estados"},
    {"csv": "data/area colhida/passo2/area_colhida_meso.csv",           "tabela": "area_colhida_mesorregioes",    "tipo": "mesorregioes"},
    {"csv": "data/area colhida/passo2/area_colhida_micro.csv",          "tabela": "area_colhida_microrregioes",   "tipo": "microrregioes"},
]

# Processamento
for item in arquivos_e_tabelas:
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
