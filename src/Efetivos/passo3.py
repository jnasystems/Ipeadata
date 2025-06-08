import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://www.ipeadata.gov.br/api/odata4/"

SERIES_CODIGOS = [
    ("QUANTBOVINOS", "bovinos"),
    ("QUANTEQUINOS", "equinos"),
    ("QUANTSUINOS", "suínos"),
    ("QUANTOVINOS", "ovinos"),
    ("QUANTCAPRINOS", "caprinos")
]

def obter_valores_serie(serie_codigo):
    url = f"{BASE_URL}ValoresSerie(SERCODIGO='{serie_codigo}')?$top=100000"
    try:
        response = requests.get(url, timeout=120)
        response.raise_for_status()
        return response.json()['value']
    except Exception as e:
        print(f"Erro na série {serie_codigo}: {e}")
        return []

def baixar_todas_series(series):
    """Baixa todas as séries em paralelo."""
    resultados = {}
    with ThreadPoolExecutor(max_workers=50) as executor:  # Ajuste o número conforme a capacidade/limite da API
        future_to_codigo = {executor.submit(obter_valores_serie, cod): (cod, nome) for cod, nome in series}
        for future in as_completed(future_to_codigo):
            cod, nome = future_to_codigo[future]
            try:
                resultados[(cod, nome)] = future.result()
            except Exception as exc:
                print(f"Erro ao buscar {cod}: {exc}")
                resultados[(cod, nome)] = []
    return resultados

def main():
    hierarquia = pd.read_csv('data/Efetivos/passo2/hierarquia_ibge.csv', dtype=str)
    municipios = hierarquia[hierarquia['Tipo'] == 'Município'][['Codigo', 'Nome', 'Codigo_Pai']]
    microrregioes = hierarquia[hierarquia['Tipo'] == 'Microrregião'][['Codigo', 'Nome', 'Codigo_Pai']]
    mesorregioes = hierarquia[hierarquia['Tipo'] == 'Mesorregião'][['Codigo', 'Nome', 'Codigo_Pai']]
    estados = hierarquia[hierarquia['Tipo'] == 'Estado'][['Codigo', 'Nome', 'Codigo_Pai']]
    regioes = hierarquia[hierarquia['Tipo'] == 'Região'][['Codigo', 'Nome']]

    # ETL: Baixar dados das séries EM PARALELO!
    print("Baixando todas as séries em paralelo...")
    dados_series = baixar_todas_series(SERIES_CODIGOS)

    dfs = []

    for (serie_codigo, nome_serie), dados_serie in dados_series.items():
        print(f"Processando série {serie_codigo}...")

        if not dados_serie:
            print(f"Nenhum dado encontrado para {serie_codigo}.")
            continue

if __name__ == "__main__":
    main()