import requests
import pandas as pd

BASE_URL = "http://www.ipeadata.gov.br/api/odata4/"

SERIES_CODIGOS = [
    ("VALPRODBANANA", "banana"),
    ("VALPRODAMENDOIM", "amendoim"),
    ("VALPRODARROZ", "arroz"),
    ("VALPRODBATATA", "batata-inglesa"),
    ("VALPRODCACAU", "cacau"),
    ("VALPRODCAFE", "café"),
    ("VALPRODCANA", "cana-de-açúcar"),
    ("VALORCASULOBS", "casulo de bicho-da-seda"),
    ("VALPRODCEBOLA", "cebola"),
    ("VALPRODFEIJAO", "feijão"),
    ("VALPRODFUMO", "fumo"),
    ("VALPRODLARANJA", "laranja"),
    ("VALORLEITE", "leite"),
    ("VALPRODMANDIOCA", "mandioca"),
    ("VALORMEL", "mel de abelha"),
    ("VALPRODMILHO", "milho"),
    ("VALOROVOCODORNA", "ovos de codorna"),
    ("VALOROVOGALINHA", "ovos de galinha"),
    ("VALPRODPIMENTA", "pimenta-do-reino"),
    ("VALPRODSOJA", "soja"),
    ("VALPRODTOMATE", "tomate"),
    ("VALPRODTRIGO", "trigo"),
    ("VALPRODUVA", "uva")
]

def obter_valores_serie(serie_codigo):
    url = f"{BASE_URL}ValoresSerie(SERCODIGO='{serie_codigo}')?$top=1000000"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['value']

def montar_nome_fonte_unidade(nome_serie):
    nome = f"Produção - {nome_serie} - valor"
    fonte = "Instituto Brasileiro de Geografia e Estatística"
    unidade = "Mil Reais"
    return nome, fonte, unidade

def main():
    hierarquia = pd.read_csv('data/Efetivos/passo2/hierarquia_ibge.csv', dtype=str)
    municipios = hierarquia[hierarquia['Tipo'] == 'Município'][['Codigo', 'Nome', 'Codigo_Pai']]
    micros = hierarquia[hierarquia['Tipo'] == 'Microrregião'][['Codigo', 'Nome', 'Codigo_Pai']]
    mesos = hierarquia[hierarquia['Tipo'] == 'Mesorregião'][['Codigo', 'Nome', 'Codigo_Pai']]
    estados = hierarquia[hierarquia['Tipo'] == 'Estado'][['Codigo', 'Nome', 'Codigo_Pai']]
    regioes = hierarquia[hierarquia['Tipo'] == 'Região'][['Codigo', 'Nome']]

    todos_dfs = []

    for codigo, nome_serie in SERIES_CODIGOS:
        print(f"Consultando série {codigo} ({nome_serie})...")
        dados_serie = obter_valores_serie(codigo)
        nome, fonte, unidade = montar_nome_fonte_unidade(nome_serie)

        registros = []
        for item in dados_serie:
            if item.get("VALDATA") and item.get("TERCODIGO") and item.get("VALVALOR") is not None:
                registros.append({
                    "sercodigo": item.get("SERCODIGO"),
                    "valdata": item.get("VALDATA"),
                    "tercodigo": str(item.get("TERCODIGO")),
                    "valvalor": round(float(item.get("VALVALOR")), 2),
                    "nome": nome,
                    "fonte": fonte,
                    "unidade": unidade
                })

        df_valores = pd.DataFrame(registros)
        df_valores['valdata'] = pd.to_datetime(df_valores['valdata'], errors='coerce', utc=True)
        df_valores = df_valores.dropna(subset=['valdata'])
        df_valores['ano'] = df_valores['valdata'].dt.year.astype(int)

        df = df_valores.merge(
            municipios.rename(columns={'Codigo': 'codigo_municipio', 'Nome': 'municipio', 'Codigo_Pai': 'codigo_micro'}),
            left_on='tercodigo', right_on='codigo_municipio', how='left'
        ).merge(
            micros.rename(columns={'Codigo': 'codigo_micro', 'Nome': 'microrregiao', 'Codigo_Pai': 'codigo_meso'}),
            on='codigo_micro', how='left'
        ).merge(
            mesos.rename(columns={'Codigo': 'codigo_meso', 'Nome': 'mesorregiao', 'Codigo_Pai': 'codigo_estado'}),
            on='codigo_meso', how='left'
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
            'codigo_micro', 'microrregiao',
            'codigo_meso', 'mesorregiao',
            'codigo_estado', 'estado',
            'codigo_regiao', 'regiao'
        ])

        tabela_pivot = df.pivot_table(
            index=[
                'nome', 'fonte', 'unidade',
                'codigo_brasil', 'brasil',
                'codigo_regiao', 'regiao',
                'codigo_estado', 'estado',
                'codigo_meso', 'mesorregiao',
                'codigo_micro', 'microrregiao',
                'codigo_municipio', 'municipio'
            ],
            columns='ano',
            values='valvalor',
            aggfunc='sum'
        ).reset_index()

        todos_dfs.append(tabela_pivot)

    # Junta tudo em um único DataFrame
    df_final = pd.concat(todos_dfs, ignore_index=True)

    # Ordena colunas de anos
    anos_finais = [ano for ano in range(1974, 2025)]
    for ano in anos_finais:
        if ano not in df_final.columns:
            df_final[ano] = None

    colunas_finais = [
        'nome', 'fonte', 'unidade',
        'codigo_brasil', 'brasil',
        'codigo_regiao', 'regiao',
        'codigo_estado', 'estado',
        'codigo_meso', 'mesorregiao',
        'codigo_micro', 'microrregiao',
        'codigo_municipio', 'municipio'
    ] + anos_finais

    df_final = df_final[colunas_finais]
    output_path = 'data/produção/passo3/valor_produçao_municipios.csv'
    df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n✅ Arquivo único gerado com sucesso: {output_path}")

if __name__ == "__main__":
    main()
