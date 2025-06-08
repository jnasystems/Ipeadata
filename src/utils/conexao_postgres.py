import yaml
import psycopg2

def carregar_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def obter_conexao_postgres():
    config = carregar_config()
    postgres_conf = config.get("postgresql")
    if not postgres_conf:
        raise ValueError("Configuração 'postgresql' não encontrada no config.yaml")

    return psycopg2.connect(
        host=postgres_conf["host"],
        port=postgres_conf["port"],
        user=postgres_conf["user"],
        password=postgres_conf["password"],
        dbname=postgres_conf["dbname"]
    )
