import pandas as pd

# Caminho do arquivo de entrada
arquivo_entrada = 'data/produção/passo1/quantidade_produçao_alimenticio.csv'

# Caminhos dos arquivos de saída
arquivo_saida_micro = 'data/produção/passo2/quantidade_produçao_micro.csv.csv'
arquivo_saida_meso = 'data/produção/passo2/quantidade_produçao_meso.csv'
arquivo_saida_estado = 'data/produção/passo2/quantidade_produçao_estado.csv'
arquivo_saida_regiao = 'data/produção/passo2/quantidade_produçao_regiao.csv'
arquivo_saida_brasil = 'data/produção/passo2/quantidade_produçao_brasil.csv'

# Ler CSV
df = pd.read_csv(arquivo_entrada)

# Identifica as colunas dos anos
colunas_anos = [col for col in df.columns if col.isdigit()]
coluna_efetivo = 'nome'  # Agora está em minúsculo

def agrupar_e_salvar(df, nivel, chave, colunas_remover, arquivo_saida):
    colunas = [col for col in df.columns if col not in colunas_remover]
    chaves = [coluna_efetivo, chave]
    agg_dict = {col: 'first' for col in colunas if col not in colunas_anos + chaves}
    agg_dict.update({col: 'sum' for col in colunas_anos})

    df_resultado = df[colunas].groupby(chaves, as_index=False).agg(agg_dict)
    for col in colunas_anos:
        df_resultado[col] = df_resultado[col].astype(float)

    ordem = [col for col in df.columns if col not in colunas_remover]
    df_resultado = df_resultado[ordem]
    df_resultado.to_csv(arquivo_saida, index=False, encoding='utf-8')
    print(f"Agrupamento por {nivel} concluído! Resultado salvo em: {arquivo_saida}")

# -------- AGRUPAMENTO POR MICRORREGIAO --------
agrupar_e_salvar(
    df,
    nivel="microrregioes",
    chave="microrregiao",
    colunas_remover=[
        "municipio", "codigo_municipio"
    ],
    arquivo_saida=arquivo_saida_micro
)

# -------- AGRUPAMENTO POR MESORREGIAO --------
agrupar_e_salvar(
    df,
    nivel="mesorregioes",
    chave="mesorregiao",
    colunas_remover=[
        "microrregiao", "codigo_microrregiao",
        "municipio", "codigo_municipio"
    ],
    arquivo_saida=arquivo_saida_meso
)

# -------- AGRUPAMENTO POR ESTADO --------
agrupar_e_salvar(
    df,
    nivel="estados",
    chave="estado",
    colunas_remover=[
        "mesorregiao", "codigo_mesorregiao",
        "microrregiao", "codigo_microrregiao",
        "municipio", "codigo_municipio"
    ],
    arquivo_saida=arquivo_saida_estado
)

# -------- AGRUPAMENTO POR REGIAO --------
agrupar_e_salvar(
    df,
    nivel="regioes",
    chave="regiao",
    colunas_remover=[
        "estado", "codigo_estado",
        "mesorregiao", "codigo_mesorregiao",
        "microrregiao", "codigo_microrregiao",
        "municipio", "codigo_municipio"
    ],
    arquivo_saida=arquivo_saida_regiao
)

# -------- AGRUPAMENTO POR BRASIL --------
agrupar_e_salvar(
    df,
    nivel="brasil",
    chave="brasil",
    colunas_remover=[
        "regiao", "codigo_regiao",
        "estado", "codigo_estado",
        "mesorregiao", "codigo_mesorregiao",
        "microrregiao", "codigo_microrregiao",
        "municipio", "codigo_municipio"
    ],
    arquivo_saida=arquivo_saida_brasil
)
