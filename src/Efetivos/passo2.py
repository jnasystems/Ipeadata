import pandas as pd
import requests

def gerar_hierarquia_ibge_completo():
    # 1. Consultar Estados e Regiões via API IBGE
    estados_url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
    estados_resp = requests.get(estados_url)
    estados = estados_resp.json()

    registros = []

    # Adicionar Brasil
    registros.append({
        "Codigo": "0",
        "Nome": "Brasil",
        "Tipo": "País",
        "Codigo_Pai": "",
        "Nome_Pai": ""
    })

    # Regiões únicas
    regioes_unicas = {}
    for estado in estados:
        regiao = estado['regiao']
        if regiao['id'] not in regioes_unicas:
            regioes_unicas[regiao['id']] = regiao['nome']
            registros.append({
                "Codigo": str(regiao['id']),
                "Nome": regiao['nome'],
                "Tipo": "Região",
                "Codigo_Pai": "0",
                "Nome_Pai": "Brasil"
            })

    # Estados
    for estado in estados:
        registros.append({
            "Codigo": str(estado['id']),
            "Nome": estado['nome'],
            "Tipo": "Estado",
            "Codigo_Pai": str(estado['regiao']['id']),
            "Nome_Pai": estado['regiao']['nome']
        })

    # 2. Ler base histórica de Mesorregiões e Microrregiões (IBGE 2016)
    # Simulando aqui com um CSV que já possuímos (você vai baixar e salvar localmente)
    base_ibge_old = pd.read_csv("data/Efetivos/passo1/divisao_meso_micro_municipio.csv", dtype=str)

    # Mesorregiões
    mesorregioes = base_ibge_old[['CD_MESO', 'NM_MESO', 'CD_UF', 'NM_UF']].drop_duplicates()
    for _, row in mesorregioes.iterrows():
        registros.append({
            "Codigo": row['CD_MESO'],
            "Nome": row['NM_MESO'],
            "Tipo": "Mesorregião",
            "Codigo_Pai": row['CD_UF'],
            "Nome_Pai": row['NM_UF']
        })

    # Microrregiões
    microrregioes = base_ibge_old[['CD_MICRO', 'NM_MICRO', 'CD_MESO', 'NM_MESO']].drop_duplicates()
    for _, row in microrregioes.iterrows():
        registros.append({
            "Codigo": row['CD_MICRO'],
            "Nome": row['NM_MICRO'],
            "Tipo": "Microrregião",
            "Codigo_Pai": row['CD_MESO'],
            "Nome_Pai": row['NM_MESO']
        })

    # Municípios
    municipios = base_ibge_old[['CD_MUN', 'NM_MUN', 'CD_MICRO', 'NM_MICRO']].drop_duplicates()
    for _, row in municipios.iterrows():
        registros.append({
            "Codigo": row['CD_MUN'],
            "Nome": row['NM_MUN'],
            "Tipo": "Município",
            "Codigo_Pai": row['CD_MICRO'],
            "Nome_Pai": row['NM_MICRO']
        })

    # 3. Montar o DataFrame final
    df_final = pd.DataFrame(registros)
    df_final.to_csv("data/Efetivos/passo2/hierarquia_ibge.csv", index=False, encoding='utf-8-sig')
    print("Arquivo 'hierarquia_ibge.csv' gerado com sucesso!")

if __name__ == "__main__":
    gerar_hierarquia_ibge_completo()
