import streamlit as st
import pandas as pd
import os
import re

st.set_page_config(page_title="Dashboard IPEAdata", layout="wide")

@st.cache_data
def load_data():
    dataframes_dict = {}

    paths = {
        "IBGE - Efetivo de Animais":  "data/Efetivos/passo3/efetivo_animais_municipios.csv",
        "IBGE - Produção Quantidade": "data/produção/passo1/quantidade_produçao_alimenticio.csv",
        "IBGE - Produção Valor":      "data/produção/passo3/valor_produçao_municipios.csv"
    }

    for origin_name, file_path in paths.items():
        if not os.path.exists(file_path):
            st.error(f"Erro: O arquivo '{file_path}' NÃO foi encontrado.")
            continue

        try:
            df = pd.read_csv(file_path, index_col=False)
            df["estado"] = df["estado"].astype(str)
            df["municipio"] = df["municipio"].astype(str)
            df["regiao"] = df["regiao"].astype(str)
            df["brasil"] = df["brasil"].astype(str)
            dataframes_dict[origin_name] = df
        except Exception as e:
            st.error(f"Erro ao ler {file_path}: {e}")

    return dataframes_dict

# ============================== INTERFACE ==============================
st.title("📊 Dashboard de Dados - Ipeadata")

dataframes = load_data()

# Filtros lado a lado
col1, col2 = st.columns(2)
with col1:
    origem_dados = st.selectbox("Selecione a origem dos dados:", list(dataframes.keys()))
with col2:
    granularidade = st.selectbox("Selecione a granularidade:", ["Município", "Estado", "Região", "Brasil"])

# Mapeamento correto
colunas_mapeadas = {
    "Município": "municipio",
    "Estado": "estado",
    "Região": "regiao"
}
col = colunas_mapeadas.get(granularidade)

df = dataframes.get(origem_dados)
if df is not None:
    if "nome" not in df.columns or "unidade" not in df.columns:
        st.warning("Colunas esperadas não encontradas.")

    # Série com nome simplificado
    series_unicas = df["nome"].unique()
    serie_labels = {nome: " - ".join(nome.split(" - ")[:2]) for nome in series_unicas}
    reverse_labels = {v: k for k, v in serie_labels.items()}

    col3, col4 = st.columns(2)
    with col3:
        serie_exibida = st.selectbox("Selecione a série:", sorted(serie_labels.values()))
    serie_selecionada = reverse_labels[serie_exibida]
    df_serie = df[df["nome"] == serie_selecionada]

    # Filtro por granularidade
    if granularidade == "Brasil":
        df_filtrado = df_serie.copy()
        valor_sel = "Brasil"

    elif granularidade == "Município":
        estados_disponiveis = sorted(df_serie["estado"].unique())
        col5, col6 = st.columns(2)
        with col5:
            estado_sel = st.selectbox("Selecione o estado:", estados_disponiveis)
        with col6:
            municipios_disponiveis = sorted(df_serie[df_serie["estado"] == estado_sel]["municipio"].unique())
            municipio_sel = st.selectbox("Selecione o município:", municipios_disponiveis)

        df_filtrado = df_serie[(df_serie["estado"] == estado_sel) & (df_serie["municipio"] == municipio_sel)]
        valor_sel = municipio_sel

    else:
        valores = sorted(df_serie[col].unique())
        valor_sel = st.selectbox(f"Selecione o {granularidade.lower()}:", valores)
        df_filtrado = df_serie[df_serie[col] == valor_sel]

    # ⚠️ Verifica se tem dados após o filtro
    if df_filtrado.empty:
        st.warning("⚠️ Nenhum dado disponível para essa seleção.")
        st.stop()

    # Unidade
    unidade = df_filtrado["unidade"].unique()[0] if "unidade" in df_filtrado.columns else "N/A"
    st.markdown(f"**Unidade:** {unidade}")

    # Detectar colunas de ano em dois formatos
    padrao_ano = re.compile(r"^(ano_)?\d{4}$")
    colunas_ano = [col for col in df_filtrado.columns if padrao_ano.match(col)]
    valid_anos = [col for col in colunas_ano if pd.to_numeric(df_filtrado[col], errors='coerce').notna().any()]

    if not valid_anos:
        st.warning("Sem dados numéricos disponíveis para os anos.")
    else:
        df_series = df_filtrado[valid_anos].sum().to_frame(name=f"{serie_exibida}")
        df_series.index = df_series.index.str.extract(r"(\d{4})")[0]  # extrai "2014" de "ano_2014" ou usa "2014"

        st.subheader(f"📈 Evolução temporal de {serie_exibida} - {valor_sel}")
        st.line_chart(df_series)

        st.subheader("📌 Indicadores Chave")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Total", f"{df_series.sum().iloc[0]:,.2f}", help="Soma de todos os anos disponíveis.")
        with col2:
            st.metric("🔺 Máximo", f"{df_series.max().iloc[0]:,.2f}", help="Maior valor registrado em um único ano.")
        with col3:
            st.metric("🔻 Mínimo", f"{df_series.min().iloc[0]:,.2f}", help="Menor valor registrado em um único ano.")

        # Prévia da planilha
        st.subheader("📄 Prévia dos dados filtrados")
        preview_cols = ["estado", "municipio", "regiao", "nome", "unidade"] + valid_anos
        st.dataframe(df_filtrado[preview_cols].head(10))

        # Botão de download
        csv = df_filtrado.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Baixar dados filtrados (.csv)",
            data=csv,
            file_name=f"ipeadata_{serie_exibida}_{valor_sel}.csv",
            mime="text/csv"
        )
