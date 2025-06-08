# 📊 IPEADATA - Análise e Armazenamento de Dados Agropecuários

Este projeto automatiza o download, tratamento e carregamento de dados do IPEADATA para um banco de dados PostgreSQL, com foco em temas como efetivo de animais, produção agropecuária, área colhida e despesas públicas por função.

---

## 🧱 Estrutura do Projeto

```
Ipeadata/
├── app.py                     # (Opcional) Script de execução principal
├── config.yaml                # Configurações do projeto
├── requirements.txt           # Dependências do Python
├── src/                       # Scripts de ingestão e ETL por tema
│   ├── Efetivos/
│   ├── Produção/
│   ├── Despesas/
│   ├── area colhida/
│   └── utils/                 # Funções auxiliares (ex: conexão com PostgreSQL)
├── data/                      # Dados brutos e processados
│   ├── Efetivos/
│   ├── Produção/
│   ├── Despesas/
│   └── area colhida/
```

---

## 🛠️ Pré-requisitos

- Python 3.10+
- Git
- PostgreSQL 13 ou superior

---

## 🐘 Instalação do PostgreSQL (Windows)

1. Baixe o instalador em: https://www.postgresql.org/download/windows/
2. Durante a instalação:
   - Escolha uma senha de administrador (ex: `postgres`)
   - Anote a porta (default: `5432`)
   - Marque a opção para instalar o **pgAdmin**
3. Após a instalação, crie um banco de dados chamado `ipeadata`:

   ```sql
   CREATE DATABASE ipeadata;
   ```

---

## ⚙️ Configuração do Projeto

1. Clone este repositório:

   ```bash
   git clone https://github.com/seu-usuario/Ipeadata.git
   cd Ipeadata
   ```

2. Crie um ambiente virtual:

   ```bash
   python -m venv .venv
   source .venv/bin/activate     # Linux/macOS
   .venv\Scripts\activate      # Windows
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure a conexão PostgreSQL no arquivo `src/utils/config.yaml`. Exemplo:

   ```python
   import psycopg2

   def obter_conexao_postgres():
       return psycopg2.connect(
           host="localhost",
           database="ipeadata",
           user="postgres",
           password="SUA_SENHA"
       )
   ```

---

## 🚀 Execução dos Scripts

Os scripts estão organizados em **passos numerados** por tema.

### 🔹 Efetivo de Animais

```bash
python src/Efetivos/passo1.py
python src/Efetivos/passo2.py
python src/Efetivos/passo3.py
python src/Efetivos/passo4.py
python src/Efetivos/passo5.py
```

### 🔹 Produção Agropecuária

```bash
python src/Produção/passo1.py
python src/Produção/passo2.py
python src/Produção/passo3.py
python src/Produção/passo4.py
python src/Produção/passo5.py
```

### 🔹 Despesas Públicas

```bash
python src/Despesas/passo1.py
python src/Despesas/passo2.py
```

### 🔹 Área Colhida

```bash
python src/area colhida/passo1.py
python src/area colhida/passo2.py
python src/area colhida/passo3.py
```

---

## 📦 Dependências Principais

- `pandas`
- `psycopg2`
- `requests`
- `pyyaml`

Veja `requirements.txt` para a lista completa.

---

## 📌 Observações

- Todos os dados são públicos (fonte: IPEADATA.gov.br).
- Os scripts criam as tabelas automaticamente se não existirem.
- Certifique-se de que o banco esteja rodando antes de executar qualquer script.

---

