import pandas as pd
import os

# Caminho do arquivo de entrada (área colhida)
arquivo_entrada = 'data/area colhida/passo1/area_colhida_municipios.csv'

# Caminhos dos arquivos de saída
arquivo_saida_micro = 'data/area colhida/passo2/area_colhida_micro.csv'
arquivo_saida_meso = 'data/area colhida/passo2/area_colhida_meso.csv'
arquivo_saida_estado = 'data/area colhida/passo2/area_colhida_estado.csv'
arquivo_saida_regiao = 'data/area colhida/passo2/area_colhida_regiao.csv'
arquivo_saida_brasil = 'data/area colhida/passo2/area_colhida_brasil.csv'

# Cria o diretório de saída se não existir
os.makedirs('data/area colhida/passo2', exist_ok=True)

# Ler CSV
df = pd.read_csv(arquivo_entrada)

# Identifica as colunas dos anos
colunas_anos = [col for col in df.columns if col.isdigit()]
coluna_cultura = 'nome'

def agrupar_e_salvar(df, nivel, chave, colunas_remover, arquivo_saida):
    colunas = [col for col in df.columns if col not in colunas_remover]
    chaves = [coluna_cultura, chave]
    agg_dict = {col: 'first' for col in colunas if col not in colunas_anos + chaves}
    agg_dict.update({col: 'sum' for col in colunas_anos})

    df_resultado = df[colunas].groupby(chaves, as_index=False).agg(agg_dict)
    for col in colunas_anos:
        df_resultado[col] = df_resultado[col].astype(float)

    ordem = [col for col in df.columns if col not in colunas_remover]
    df_resultado = df_resultado[ordem]
    df_resultado.to_csv(arquivo_saida, index=False, encoding='utf-8-sig')
    print(f"Agrupamento por {nivel} concluído! Resultado salvo em: {arquivo_saida}")

# -------- AGRUPAMENTO POR MICRORREGIÃO --------
agrupar_e_salvar(
    df, "microrregião", "microrregiao",
    ["municipio", "codigo_municipio"],
    arquivo_saida_micro
)

# -------- AGRUPAMENTO POR MESORREGIÃO --------
agrupar_e_salvar(
    df, "mesorregião", "mesorregiao",
    ["microrregiao", "codigo_microrregiao", "municipio", "codigo_municipio"],
    arquivo_saida_meso
)

# -------- AGRUPAMENTO POR ESTADO --------
agrupar_e_salvar(
    df, "estado", "estado",
    ["mesorregiao", "codigo_mesorregiao", "microrregiao", "codigo_microrregiao", "municipio", "codigo_municipio"],
    arquivo_saida_estado
)

# -------- AGRUPAMENTO POR REGIÃO --------
agrupar_e_salvar(
    df, "região", "regiao",
    ["estado", "codigo_estado", "mesorregiao", "codigo_mesorregiao", "microrregiao", "codigo_microrregiao", "municipio", "codigo_municipio"],
    arquivo_saida_regiao
)

# -------- AGRUPAMENTO POR BRASIL --------
agrupar_e_salvar(
    df, "brasil", "brasil",
    ["regiao", "codigo_regiao", "estado", "codigo_estado", "mesorregiao", "codigo_mesorregiao", "microrregiao", "codigo_microrregiao", "municipio", "codigo_municipio"],
    arquivo_saida_brasil
)
