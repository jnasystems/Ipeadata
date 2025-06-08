import requests
import pandas as pd

BASE_URL = "http://www.ipeadata.gov.br/api/odata4/"

SERIES_CODIGOS = [
    ("QUANTPRODBANANA", "Banana"),
    ("QUANTPRODAMENDOIM", "Amendoim"),
    ("QUANTPRODARROZ", "Arroz"),
    ("QUANTPRODBATATA", "Batata-inglesa"),
    ("QUANTPRODCACAU", "Cacau"),
    ("QUANTPRODCAFE", "Café"),
    ("QUANTPRODCANA", "Cana-de-açúcar"),
    ("QUANTCASULOBS", "Casulo de bicho-da-seda"),
    ("QUANTPRODCEBOLA", "Cebola"),
    ("QUANTPRODFEIJAO", "Feijão"),
    ("QUANTPRODFUMO", "Fumo"),
    ("QUANTLA", "Lã"),
    ("QUANTPRODLARANJA", "Laranja"),
    ("QUANTLEITE", "Leite"),
    ("QUANTPRODMANDIOCA", "Mandioca"),
    ("QUANTMEL", "Mel de abelha"),
    ("QUANTPRODMILHO", "Milho"),
    ("QUANTOVOCODORNA", "Ovos de codorna"),
    ("QUANTOVOGALINHA", "Ovos de galinha"),
    ("QUANTPRODPIMENTA", "Pimenta-do-reino"),
    ("QUANTPRODSOJA", "Soja"),
    ("QUANTPRODTOMATE", "Tomate"),
    ("QUANTPRODTRIGO", "Trigo"),
    ("QUANTPRODUVA", "Uva")
]

def obter_valores_serie(serie_codigo):
    url = f"{BASE_URL}ValoresSerie(SERCODIGO='{serie_codigo}')?$top=100000"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['value']
    else:
        print(f"Erro ao acessar a API: {response.status_code}")
        return []

def montar_nome_fonte_unidade(serie_codigo, nome_serie):
    nome_formatado = nome_serie.capitalize()
    if "QUANTPROD" in serie_codigo:
        nome = f"Produção - {nome_formatado} - Tonelada"
        unidade = "Tonelada"
    elif "VALPROD" in serie_codigo:
        nome = f"Produção - {nome_formatado} - R$ a preço do ano"
        unidade = "R$ a preço do ano"
    else:
        nome = f"Série desconhecida - {nome_formatado}"
        unidade = "Desconhecida"
    fonte = "Instituto Brasileiro de Geografia e Estatística"
    return nome, fonte, unidade

def main():
    hierarquia = pd.read_csv('data/Efetivos/passo2/hierarquia_ibge.csv', dtype=str)
    municipios = hierarquia[hierarquia['Tipo'] == 'Município'][['Codigo', 'Nome', 'Codigo_Pai']]
    microrregioes = hierarquia[hierarquia['Tipo'] == 'Microrregião'][['Codigo', 'Nome', 'Codigo_Pai']]
    mesorregioes = hierarquia[hierarquia['Tipo'] == 'Mesorregião'][['Codigo', 'Nome', 'Codigo_Pai']]
    estados = hierarquia[hierarquia['Tipo'] == 'Estado'][['Codigo', 'Nome', 'Codigo_Pai']]
    regioes = hierarquia[hierarquia['Tipo'] == 'Região'][['Codigo', 'Nome']]

    dfs_quant = []
    dfs_valor = []

    for serie_codigo, nome_serie in SERIES_CODIGOS:
        print(f"\n Consultando série {serie_codigo}...")

        dados_serie = obter_valores_serie(serie_codigo)
        if not dados_serie:
            print(f" Nenhum dado encontrado para {serie_codigo}.")
            continue

        nome, fonte, unidade = montar_nome_fonte_unidade(serie_codigo, nome_serie)

        registros = [
            {
                "sercodigo": item.get("SERCODIGO"),
                "valdata": item.get("VALDATA"),
                "tercodigo": str(item.get("TERCODIGO")),
                "valvalor": item.get("VALVALOR")
            }
            for item in dados_serie
            if item.get("VALDATA") and item.get("TERCODIGO")
        ]
        df_valores = pd.DataFrame(registros)

        if df_valores.empty:
            print(f" Nenhum valor válido encontrado para {serie_codigo}.")
            continue

        df_valores['ano'] = pd.to_datetime(df_valores['valdata'], utc=True, errors='coerce').dt.year
        df_valores = df_valores.dropna(subset=['ano'])
        df_valores['ano'] = df_valores['ano'].astype(int)
        df_valores['tercodigo'] = df_valores['tercodigo'].astype(str)

        # 🧠 Filtro para considerar apenas códigos de municípios válidos
        codigos_validos = set(municipios['Codigo'])
        df_valores = df_valores[df_valores['tercodigo'].isin(codigos_validos)]

        # 🧠 Remover duplicatas por município e ano
        df_valores = df_valores.drop_duplicates(subset=['tercodigo', 'ano'])

        # 💬 Diagnóstico (opcional)
        codigos_ausentes = set(df_valores['tercodigo']) - codigos_validos
        if codigos_ausentes:
            print(f" {len(codigos_ausentes)} códigos TERCODIGO não encontrados na hierarquia.")

        # Merge com a hierarquia
        df = df_valores.merge(
            municipios.rename(columns={'Codigo': 'codigo_municipio', 'Nome': 'municipio', 'Codigo_Pai': 'codigo_microrregiao'}),
            left_on='tercodigo', right_on='codigo_municipio', how='left'
        ).merge(
            microrregioes.rename(columns={'Codigo': 'codigo_microrregiao', 'Nome': 'microrregiao', 'Codigo_Pai': 'codigo_mesorregiao'}),
            on='codigo_microrregiao', how='left'
        ).merge(
            mesorregioes.rename(columns={'Codigo': 'codigo_mesorregiao', 'Nome': 'mesorregiao', 'Codigo_Pai': 'codigo_estado'}),
            on='codigo_mesorregiao', how='left'
        ).merge(
            estados.rename(columns={'Codigo': 'codigo_estado', 'Nome': 'estado', 'Codigo_Pai': 'codigo_regiao'}),
            on='codigo_estado', how='left'
        ).merge(
            regioes.rename(columns={'Codigo': 'codigo_regiao', 'Nome': 'regiao'}),
            on='codigo_regiao', how='left'
        )

        df['codigo_brasil'] = '0'
        df['brasil'] = 'brasil'

        df = df.dropna(subset=[
            'codigo_municipio', 'municipio',
            'codigo_microrregiao', 'microrregiao',
            'codigo_mesorregiao', 'mesorregiao',
            'codigo_estado', 'estado',
            'codigo_regiao', 'regiao'
        ])

        print(f" Registros válidos: {len(df)}")

        tabela_pivot = df.pivot_table(
            index=[
                'codigo_brasil', 'brasil',
                'codigo_regiao', 'regiao',
                'codigo_estado', 'estado',
                'codigo_mesorregiao', 'mesorregiao',
                'codigo_microrregiao', 'microrregiao',
                'codigo_municipio', 'municipio'
            ],
            columns='ano',
            values='valvalor',
            aggfunc='sum'
        ).reset_index()

        tabela_pivot.insert(0, 'unidade', unidade)
        tabela_pivot.insert(0, 'fonte', fonte)
        tabela_pivot.insert(0, 'nome', nome)

        anos_finais = list(range(1974, 2024))
        for ano in anos_finais:
            if ano not in tabela_pivot.columns:
                tabela_pivot[ano] = None
            else:
                tabela_pivot[ano] = tabela_pivot[ano].round(2)

        colunas_final = [
            'nome', 'fonte', 'unidade',
            'codigo_brasil', 'brasil',
            'codigo_regiao', 'regiao',
            'codigo_estado', 'estado',
            'codigo_mesorregiao', 'mesorregiao',
            'codigo_microrregiao', 'microrregiao',
            'codigo_municipio', 'municipio'
        ] + anos_finais

        tabela_pivot = tabela_pivot[colunas_final]

        if serie_codigo.startswith("QUANTPROD"):
            dfs_quant.append(tabela_pivot)
        elif serie_codigo.startswith("VALPROD"):
            dfs_valor.append(tabela_pivot)

    if dfs_quant:
        tabela_quant = pd.concat(dfs_quant, ignore_index=True)
        path_quant = "data/produção/passo1/quantidade_produçao_alimenticio.csv"
        tabela_quant.to_csv(path_quant, index=False, encoding='utf-8-sig')
        print(f" Arquivo de quantidade gerado: {path_quant}")
    else:
        print(" Nenhuma série de quantidade exportada.")

    # if dfs_valor:
    #     tabela_valor = pd.concat(dfs_valor, ignore_index=True)
    #     path_valor = "data/produção/passo1/valor_produçao_alimenticio.csv"
    #     tabela_valor.to_csv(path_valor, index=False, encoding='utf-8-sig')
    #     print(f" Arquivo de valor gerado: {path_valor}")
    # else:
    #     print(" Nenhuma série de valor exportada.")

if __name__ == "__main__":
    main()
