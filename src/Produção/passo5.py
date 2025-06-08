import sys
import os
import csv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.conexao_postgres import obter_conexao_postgres  # Função externa

# Gera anos com prefixo para o banco
anos_colunas = [f"ano_{ano}" for ano in range(1974, 2025)]

# Schemas simples por tipo (nomes de colunas para o banco)
schemas = {
    "municipio": [
        "nome", "fonte", "unidade", "codigo_brasil", "brasil", "codigo_regiao", "regiao",
        "codigo_estado", "estado", "codigo_mesorregiao", "mesorregiao", "codigo_microrregiao",
        "microrregiao", "codigo_municipio", "municipio", *anos_colunas
    ],
    "brasil": [
        "nome", "fonte", "unidade", "codigo_brasil", "brasil", *anos_colunas
    ],
    "regioes": [
        "nome", "fonte", "unidade", "codigo_brasil", "brasil", "codigo_regiao", "regiao", *anos_colunas
    ],
    "estados": [
        "nome", "fonte", "unidade", "codigo_brasil", "brasil", "codigo_regiao", "regiao",
        "codigo_estado", "estado", *anos_colunas
    ],
    "mesorregioes": [
        "nome", "fonte", "unidade", "codigo_brasil", "brasil", "codigo_regiao", "regiao",
        "codigo_estado", "estado", "codigo_mesorregiao", "mesorregiao", *anos_colunas
    ],
    "microrregioes": [
        "nome", "fonte", "unidade", "codigo_brasil", "brasil", "codigo_regiao", "regiao",
        "codigo_estado", "estado", "codigo_mesorregiao", "mesorregiao", "codigo_microrregiao",
        "microrregiao", *anos_colunas
    ]
}

def corrigir_csv_estrutura(caminho_entrada, caminho_saida, schema):
    with open(caminho_entrada, encoding="utf-8") as f_in:
        leitor = list(csv.reader(f_in))

    colunas_csv = leitor[0]
    colunas_esperadas = len(schema)

    with open(caminho_saida, "w", newline='', encoding="utf-8") as f_out:
        escritor = csv.writer(f_out)
        escritor.writerow(schema)  # sobrescreve com colunas adaptadas (ano_1974, etc.)

        for linha in leitor[1:]:
            diff = colunas_esperadas - len(linha)
            if diff > 0:
                linha += [""] * diff
            elif diff < 0:
                linha = linha[:colunas_esperadas]
            escritor.writerow(linha)

def criar_tabela_se_nao_existir(cursor, tabela, colunas):
    colunas_sql = ', '.join(f'"{col}" TEXT' for col in colunas)
    sql = f'CREATE TABLE IF NOT EXISTS "{tabela}" ({colunas_sql});'
    cursor.execute(sql)

def inserir_csv_postgres(caminho_csv, tabela, colunas):
    conn = obter_conexao_postgres()
    cursor = conn.cursor()

    # Criação automática da tabela
    criar_tabela_se_nao_existir(cursor, tabela, colunas)

    with open(caminho_csv, encoding="utf-8") as f:
        leitor = csv.reader(f)
        next(leitor)  # pula cabeçalho original

        placeholders = ','.join(['%s'] * len(colunas))
        cols = ','.join([f'"{col}"' for col in colunas])  # aspas duplas por segurança
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
    {"csv": "data/produção/passo1/quantidade_produçao_alimenticio.csv",    "tabela": "quant_prod_municipios",      "tipo": "municipio"},
    {"csv": "data/produção/passo2/quantidade_produçao_brasil.csv",         "tabela": "quant_prod_brasil",          "tipo": "brasil"},
    {"csv": "data/produção/passo2/quantidade_produçao_regiao.csv",         "tabela": "quant_prod_regioes",         "tipo": "regioes"},
    {"csv": "data/produção/passo2/quantidade_produçao_estado.csv",         "tabela": "quant_prod_estados",         "tipo": "estados"},
    {"csv": "data/produção/passo2/quantidade_produçao_meso.csv",           "tabela": "quant_prod_mesorregioes",    "tipo": "mesorregioes"},
    {"csv": "data/produção/passo2/quantidade_produçao_micro.csv",          "tabela": "quant_prod_microrregioes",   "tipo": "microrregioes"},
    {"csv": "data/produção/passo3/valor_produçao_municipios.csv",          "tabela": "valor_prod_municipios",      "tipo": "municipio"},
    {"csv": "data/produção/passo3/valor_produçao_brasil.csv",              "tabela": "valor_prod_brasil",          "tipo": "brasil"},
    {"csv": "data/produção/passo3/valor_produçao_regiao.csv",              "tabela": "valor_prod_regioes",         "tipo": "regioes"},
    {"csv": "data/produção/passo3/valor_produçao_estado.csv",              "tabela": "valor_prod_estados",         "tipo": "estados"},
    {"csv": "data/produção/passo3/valor_produçao_meso.csv",                "tabela": "valor_prod_mesorregioes",    "tipo": "mesorregioes"},
    {"csv": "data/produção/passo3/valor_produçao_micro.csv",               "tabela": "valor_prod_microrregioes",   "tipo": "microrregioes"},
]

# Processamento
for item in arquivos_e_tabelas:
    caminho = item["csv"]
    tabela = item["tabela"]
    tipo = item["tipo"]
    colunas = schemas[tipo]

    print(f"🔧 Corrigindo: {caminho}")
    corrigir_csv_estrutura(caminho, caminho, colunas)

    print(f"📤 Inserindo em: {tabela}")
    try:
        inserir_csv_postgres(caminho, tabela, colunas)
    except Exception as e:
        print(f"❌ Erro ao inserir em {tabela}: {e}")
