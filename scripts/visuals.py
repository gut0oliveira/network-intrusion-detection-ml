# scripts/visuals.py

import streamlit as st

def aplicar_estilo():
    st.set_page_config(
        page_title="Engenharia Reversa de Malware",
        page_icon="👨🏻‍💻",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    esconder_streamlit()
    tema_dark()

def esconder_streamlit():
    hide_streamlit_style = """
        <style>
        #MainMenu {visibility: visible;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def tema_dark():
    tema_dark = """
        <style>
        body, .stApp {
            background-color: #0E1117;
            color: #FFFFFF;
            font-family: 'Segoe UI', sans-serif;
        }
        .stButton>button {
            background-color: #1E90FF;
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            border: none;
            font-size: 16px;
        }
        .stButton>button:hover {
            background-color: #00BFFF;
        }
        .stFileUploader, .stSelectbox, .stTextInput, .stNumberInput, .stDateInput, .stTimeInput {
            background-color: #1C1F26;
            color: #FFFFFF;
            border: 1px solid #333;
            border-radius: 10px;
            padding: 8px;
        }
        .stPlotlyChart, .stPyplotChart {
            background-color: #0E1117;
        }
        </style>
    """
    st.markdown(tema_dark, unsafe_allow_html=True)

def titulo(titulo):
    st.markdown(f"<h1 style='text-align: center; color: #FFFFFF;'>{titulo}</h1>", unsafe_allow_html=True)
    st.markdown("---")

def upload_arquivo():
    st.subheader("Upload do arquivo:")
    arquivo = st.file_uploader("", type=["csv"])
    if arquivo is None:
        st.warning("ℹ️ Faça o upload para continuar.")
    return arquivo

def rodape(nome, ra):
    st.markdown("---")
    st.markdown(
        f"<h5 style='text-align: center;'>Desenvolvido por {nome} • RA: {ra}</h5>",
        unsafe_allow_html=True
    )

def sidebar_info():
    with st.sidebar:
        st.markdown("## Projeto Integrador IV")
        st.markdown("---")
        st.write(
            """
            Este aplicativo utiliza modelos de Machine Learning
            para prever possíveis ataques cibernéticos com base
            em características de tráfego de rede.
            """
        )
        st.markdown("---")
        st.markdown("## Desenvolvimento")
        st.markdown("---")
        st.write(
            """
            Este aplicativo foi desenvolvido em 4 etapas principais, são elas:
            """
        )
        st.markdown(
            """
            1. Pré-processamento de Dados
            2. Análise Exploratória de Dados
            3. Engenharia de Atributos
            4. Treinamento e Avaliação
            """
        )
        st.markdown("---")
