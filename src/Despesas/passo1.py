import requests
import pandas as pd
import os

# Diretório base do projeto (relativo ao script atual)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Caminhos relativos
EFETIVO_PATH = os.path.join(BASE_DIR, "data", "Efetivos", "passo3", "efetivo_animais_municipios.csv")
DESPESAS_DIR = os.path.join(BASE_DIR, "data", "despesas", "passo1")

# URL da API
BASE_URL = "http://ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='{}')?$top=100000"

# Séries e arquivos de saída
SERIES = {
    "DFAGRE": {"tipo": "Estado", "arquivo": os.path.join(DESPESAS_DIR, "despesa_estado.csv")},
    "DFAGRM": {"tipo": "Município", "arquivo": os.path.join(DESPESAS_DIR, "despesa_municipio.csv")}
}

def obter_despesa(sercodigo):
    print(f"🔍 Consultando API para a série: {sercodigo}")
    response = requests.get(BASE_URL.format(sercodigo))
    if response.status_code != 200:
        print(f"❌ Erro na série {sercodigo}: {response.status_code}")
        return pd.DataFrame()

    df = pd.DataFrame(response.json().get("value", []))
    if df.empty:
        print(f"⚠️ Nenhum dado retornado para {sercodigo}")
        return pd.DataFrame()

    df['ano'] = pd.to_datetime(df['VALDATA'], errors='coerce', utc=True).dt.year
    df = df[['TERCODIGO', 'ano', 'VALVALOR']].rename(columns={
        'TERCODIGO': 'codigo_ibge',
        'VALVALOR': 'valor'
    })
    df['codigo_ibge'] = df['codigo_ibge'].astype(str)
    return df

def carregar_codigos_efetivo():
    return pd.read_csv(EFETIVO_PATH, dtype=str)[[
        'codigo_estado', 'estado', 'codigo_municipio', 'municipio'
    ]].drop_duplicates()

def processar_dados(df_despesa, df_efetivo, tipo_unidade):
    df_despesa['valor'] = pd.to_numeric(df_despesa['valor'], errors='coerce')

    if tipo_unidade == "Estado":
        df_despesa['codigo_estado'] = df_despesa['codigo_ibge'].str[:2]
        df_estados = df_efetivo[['codigo_estado', 'estado']].drop_duplicates()
        df_estados['codigo_estado'] = df_estados['codigo_estado'].astype(str).str.zfill(2)
        df = df_despesa.merge(df_estados, on='codigo_estado', how='left')
        df['tipo_unidade'] = 'Estado'
        return df[['tipo_unidade', 'codigo_estado', 'estado', 'ano', 'valor']]
    else:
        df_despesa['codigo_ibge'] = df_despesa['codigo_ibge'].astype(str)
        df_efetivo['codigo_municipio'] = df_efetivo['codigo_municipio'].astype(str)
        df = df_despesa.merge(
            df_efetivo[['codigo_estado', 'estado', 'codigo_municipio', 'municipio']],
            left_on='codigo_ibge',
            right_on='codigo_municipio',
            how='left'
        )
        df['tipo_unidade'] = 'Município'
        return df[['tipo_unidade', 'codigo_estado', 'estado', 'codigo_municipio', 'municipio', 'ano', 'valor']]

def gerar_csv(df, caminho_saida, tipo_unidade):
    if tipo_unidade == "Estado":
        index_cols = ['tipo_unidade', 'codigo_estado', 'estado']
    else:
        index_cols = ['tipo_unidade', 'codigo_estado', 'estado', 'codigo_municipio', 'municipio']

    tabela = df.pivot_table(
        index=index_cols,
        columns='ano',
        values='valor',
        aggfunc='sum'
    ).reset_index()

    tabela.insert(0, 'unidade', 'R$')
    tabela.insert(0, 'fonte', 'Ministério da Fazenda - STN')
    tabela.insert(0, 'nome', 'Despesa por função - gestão ambiental, agricultura e organização agrária')

    for ano in range(1974, 2024):
        if ano in tabela.columns:
            tabela[ano] = tabela[ano].round(0).astype("Int64")
        else:
            tabela[ano] = pd.NA

    colunas_finais = ['nome', 'fonte', 'unidade', 'tipo_unidade', 'codigo_estado', 'estado']
    if tipo_unidade == "Município":
        colunas_finais += ['codigo_municipio', 'municipio']
    colunas_finais += list(range(1974, 2024))

    tabela = tabela.reindex(columns=colunas_finais)
    tabela.to_csv(caminho_saida, index=False, encoding="utf-8-sig")
    print(f"✅ Arquivo gerado: {caminho_saida}")

def main():
    df_efetivo = carregar_codigos_efetivo()

    for sercodigo, info in SERIES.items():
        df_despesa = obter_despesa(sercodigo)
        if df_despesa.empty:
            continue

        df_tratado = processar_dados(df_despesa, df_efetivo, info["tipo"])
        gerar_csv(df_tratado, info["arquivo"], info["tipo"])

if __name__ == "__main__":
    main()
