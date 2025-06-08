import requests
import pandas as pd
import os

BASE_URL = "http://www.ipeadata.gov.br/api/odata4/"

SERIES_CODIGOS = [
    ("AREACOLALGHER", "Algodão herbáceo (caroço)"),
    ("AREACOLAMENDOIM", "Amendoim"),
    ("AREACOLARROZ", "Arroz"),
    ("AREACOLBANANA", "Banana"),
    ("AREACOLBATATA", "Batata-inglesa"),
    ("AREACOLCACAU", "Cacau"),
    ("AREACOLCAFE", "Café"),
    ("AREACOLCANA", "Cana-de-açúcar"),
    ("AREACOLCEBOLA", "Cebola"),
    ("AREACOLFEIJAO", "Feijão"),
    ("AREACOLFUMO", "Fumo"),
    ("AREACOLLARANJA", "Laranja"),
    ("AREACOLPERM", "Lavoura permanente"),
    ("AREACOLTEMP", "Lavoura temporária"),
    ("AREACOLMANDIOCA", "Mandioca"),
    ("AREACOLMILHO", "Milho"),
    ("AREACOLPIMENTA", "Pimenta-do-reino"),
    ("AREACOLSOJA", "Soja"),
    ("AREACOLTOMATE", "Tomate"),
    ("AREACOLTOT", "Total"),
    ("AREACOLTRIGO", "Trigo"),
    ("AREACOLUVA", "Uva"),
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
    if "AREACOL" in serie_codigo:
        nome = f"Área colhida - {nome_formatado} - hectare"
        unidade = "hectare"
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

    dfs_area = []

    for serie_codigo, nome_serie in SERIES_CODIGOS:
        print(f" Consultando série {serie_codigo}...")

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
            continue

        df_valores['ano'] = pd.to_datetime(df_valores['valdata'], utc=True, errors='coerce').dt.year
        df_valores = df_valores.dropna(subset=['ano'])
        df_valores['ano'] = df_valores['ano'].astype(int)
        df_valores['tercodigo'] = df_valores['tercodigo'].astype(str)

        codigos_validos = set(municipios['Codigo'])
        df_valores = df_valores[df_valores['tercodigo'].isin(codigos_validos)]
        df_valores = df_valores.drop_duplicates(subset=['tercodigo', 'ano'])

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
        dfs_area.append(tabela_pivot)

    if dfs_area:
        tabela_area = pd.concat(dfs_area, ignore_index=True)
        os.makedirs("data/area colhida/passo1", exist_ok=True)
        path_area = "data/area colhida/passo1/area_colhida_municipios.csv"
        tabela_area.to_csv(path_area, index=False, encoding='utf-8-sig')
        print(f" Arquivo de área colhida gerado: {path_area}")
    else:
        print(" Nenhuma série de área colhida exportada.")

if __name__ == "__main__":
    main()
