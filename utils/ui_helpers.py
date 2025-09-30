"""
Funções utilitárias para a UI: carregamento de instância e criação de placeholders de plot.
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def show_instance_loader():
    """Mostra gerador de instância e uploader. Retorna um DataFrame ou None."""
    config_path = "configs/instance_config.yaml"
    output_path = "data/processed/instance.csv"

    if st.button("🔄 Gerar nova instância"):
        try:
            from generate_instance import generate_instance
            from validate_instance import validate_instance
            generate_instance(config_path=config_path, output_path=output_path)
            st.success(f"Instância gerada com sucesso em: {output_path}")

            resultado = validate_instance(output_path)
            if "✅" in resultado:
                st.success(f"Validação: {resultado}")
            else:
                st.error(f"Validação falhou: {resultado}")

            df = pd.read_csv(output_path)
            st.session_state["df"] = df

            with open(output_path, "r") as f:
                st.download_button("📥 Baixar CSV", f.read(), file_name="instance.csv")

        except Exception as e:
            st.error(f"Erro: {e}")

    uploaded_file = st.file_uploader("Ou carregue um arquivo CSV manualmente:", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.session_state["df"] = df

    return st.session_state.get("df")

def create_plot_placeholders():
    col1, col2 = st.columns(2)  # duas colunas lado a lado
    with col1:
        plot_placeholder1 = st.empty()
    with col2:
        plot_placeholder2 = st.empty()

    fig1, ax1 = plt.subplots(figsize=(5, 4))
    fig2, ax2 = plt.subplots(figsize=(5, 4))

    plot_placeholders = {"p1": plot_placeholder1, "p2": plot_placeholder2}
    figs_axes = (fig1, ax1, fig2, ax2)
    return plot_placeholders, figs_axes
