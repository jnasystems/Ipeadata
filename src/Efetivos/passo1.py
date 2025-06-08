import pandas as pd
import requests

def baixar_divisao_meso_micro_municipio():
    # Baixar a lista de municípios (com microrregião e mesorregião)
    url_municipios = "https://servicodados.ibge.gov.br/api/v2/malhas/?formato=application/vnd.ibge.municipio+json"
    
    print("Baixando lista de municípios (malha)...")

    # Como a API pública não oferece esse JSON diretamente estruturado, vamos construir manualmente

    # Outra alternativa: usar a API localidades/municipios e enriquecer
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
    response = requests.get(url)
    if response.status_code != 200:
        print("Erro ao acessar a API de municípios do IBGE!")
        return
    
    municipios = response.json()

    registros = []

    for municipio in municipios:
        registros.append({
            "CD_UF": municipio['microrregiao']['mesorregiao']['UF']['id'],
            "NM_UF": municipio['microrregiao']['mesorregiao']['UF']['nome'],
            "CD_MESO": municipio['microrregiao']['mesorregiao']['id'],
            "NM_MESO": municipio['microrregiao']['mesorregiao']['nome'],
            "CD_MICRO": municipio['microrregiao']['id'],
            "NM_MICRO": municipio['microrregiao']['nome'],
            "CD_MUN": municipio['id'],
            "NM_MUN": municipio['nome']
        })

    df = pd.DataFrame(registros)

    # Salvar no CSV
    df.to_csv('data/Efetivos/passo1/ivisao_meso_micro_municipio.csv', index=False, encoding='utf-8-sig')
    print("Arquivo 'divisao_meso_micro_municipio.csv' gerado com sucesso!")

if __name__ == "__main__":
    baixar_divisao_meso_micro_municipio()
