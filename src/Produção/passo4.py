import pandas as pd

# Caminho do arquivo gerado no passo anterior
arquivo_entrada = 'data/produção/passo3/valor_produçao_municipios.csv'

# Caminhos dos arquivos de saída
saida_micro = 'data/produção/passo3/valor_produçao_micro.csv'
saida_meso = 'data/produção/passo3/valor_produçao_meso.csv'
saida_estado = 'data/produção/passo3/valor_produçao_estado.csv'
saida_regiao = 'data/produção/passo3/valor_produçao_regiao.csv'
saida_brasil = 'data/produção/passo3/valor_produçao_brasil.csv'

# Leitura do arquivo base
df = pd.read_csv(arquivo_entrada)

# Detectar colunas de ano (números)
col_anos = [col for col in df.columns if col.isdigit()]

def agrupar(df, nivel, chave, remover, saida):
    print(f"Agrupando por {nivel}...")
    
    colunas_usar = [col for col in df.columns if col not in remover]
    chaves = ['nome', chave]
    agg_dict = {col: 'first' for col in colunas_usar if col not in chaves + col_anos}
    agg_dict.update({col: 'sum' for col in col_anos})

    df_resultado = df[colunas_usar].groupby(chaves, as_index=False).agg(agg_dict)

    # ✅ Arredondar os valores numéricos para 2 casas decimais
    df_resultado[col_anos] = df_resultado[col_anos].round(2)

    # Ordenar colunas como estavam no original
    ordem = [col for col in df.columns if col not in remover]
    df_resultado = df_resultado[ordem]

    df_resultado.to_csv(saida, index=False, encoding='utf-8-sig')
    print(f"✅ {nivel} salvo em: {saida}")

# Microrregiões
agrupar(df, 'microrregiões', 'microrregiao', ['municipio', 'codigo_municipio'], saida_micro)

# Mesorregiões
agrupar(df, 'mesorregiões', 'mesorregiao', ['municipio', 'codigo_municipio', 'microrregiao', 'codigo_micro'], saida_meso)

# Estados
agrupar(df, 'estados', 'estado', ['municipio', 'codigo_municipio', 'microrregiao', 'codigo_micro', 'mesorregiao', 'codigo_meso'], saida_estado)

# Regiões
agrupar(df, 'regiões', 'regiao', ['municipio', 'codigo_municipio', 'microrregiao', 'codigo_micro', 'mesorregiao', 'codigo_meso', 'estado', 'codigo_estado'], saida_regiao)

# Brasil
agrupar(df, 'Brasil', 'brasil', ['municipio', 'codigo_municipio', 'microrregiao', 'codigo_micro', 'mesorregiao', 'codigo_meso', 'estado', 'codigo_estado', 'regiao', 'codigo_regiao'], saida_brasil)
