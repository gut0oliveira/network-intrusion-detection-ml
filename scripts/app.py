from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import streamlit as st
from inference import load_bundle, predict, MODEL_PATH
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from visuals import aplicar_estilo, titulo, upload_arquivo, rodape, sidebar_info

aplicar_estilo()
titulo("Detecção de Intrusões em Tráfego de Rede")
sidebar_info()

@st.cache_resource
def carregar_modelos(path, modified):
    return load_bundle(path)

if not MODEL_PATH.exists():
    st.info("Modelos corrigidos ainda não foram treinados. Execute os notebooks e gere models/modelos.pkl.")
    st.stop()
try:
    bundle = carregar_modelos(MODEL_PATH, MODEL_PATH.stat().st_mtime_ns)
except Exception as error:
    st.error(f"Não foi possível carregar o artefato: {error}")
    st.stop()

st.caption("Selecione explicitamente a tarefa. O rótulo do CSV, quando presente, não é usado para prever.")
tipo = st.radio("Tipo de classificação", ["Binário", "Multiclasse"])
nome = st.selectbox("Modelo", list(bundle["models"][tipo]))
arquivo = upload_arquivo()
if arquivo is not None:
    try:
        frame = pd.read_csv(arquivo)
        st.dataframe(frame.head())
        if st.button("Realizar previsão"):
            result = predict(bundle["models"][tipo][nome], frame)
            st.dataframe(result)
            counts = result["Previsão"].value_counts()
            st.subheader("Quantidade de registros por classe")
            st.bar_chart(counts)
            if tipo == "Multiclasse":
                fig, ax = plt.subplots(figsize=(10, 5))
                sns.heatmap(result.drop(columns="Previsão").head(20), annot=True, fmt=".2f", ax=ax)
                st.pyplot(fig)
                plt.close(fig)
            st.download_button("Baixar previsões", result.to_csv(index=False).encode("utf-8"), "previsoes.csv", "text/csv")
    except Exception as error:
        st.error(f"Erro ao processar CSV: {error}")
rodape("Augusto Oliveira", "22153474")
