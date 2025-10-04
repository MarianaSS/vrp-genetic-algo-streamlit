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

    with st.expander("Criar ou carregar instância", expanded=False):
        st.markdown("### Crie uma nova instância")
        st.markdown(
            """
            - O **ponto 0** representa o **depósito fixo**.
            - Os demais pontos são os **clientes** a serem atendidos.
            - Apenas instâncias com **até 10 pontos (incluindo depósito)** 
              serão usadas para comparação com a **solução brute force**.
            """
        )

        # Slider para número de pontos a serem gerados
        n_points = st.slider(
            "Número de clientes da instância (sem contar o depósito)",
            min_value=5,
            max_value=50,
            value=9,
        )

        if st.button("Gerar nova instância"):
            try:
                from generate_instance import generate_instance
                from validate_instance import validate_instance

                generate_instance(
                    config_path=config_path,
                    output_path=output_path,
                    n_points=n_points,
                )
                st.success(
                    f"Instância com {n_points} clientes + depósito (total {n_points + 1} pontos) gerada em: {output_path}"
                )

                resultado = validate_instance(output_path)
                if "✅" in resultado:
                    st.success(f"Validação: {resultado}")
                else:
                    st.error(f"Validação falhou: {resultado}")

                df = pd.read_csv(output_path)
                st.session_state["df"] = df

                with open(output_path, "r") as f:
                    st.download_button(
                        "📥 Baixar CSV",
                        f.read(),
                        file_name="instance.csv",
                    )

            except Exception as e:
                st.error(f"Erro: {e}")

        st.markdown("---")
        st.markdown("### Ou carregue uma instância existente")
        uploaded_file = st.file_uploader(
            "Selecione um arquivo CSV de instância:", type="csv"
        )
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
