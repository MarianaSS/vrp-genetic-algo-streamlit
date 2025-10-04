"""
UI do Streamlit. Responsável por montar a interface, coletar parâmetros
e chamar o serviço que executa o GA.
"""
import streamlit as st
import io

from services.ga_runner import run_ga_and_build_report
from utils.ui_helpers import show_instance_loader, create_plot_placeholders
from reporting.llm_reporter import generate_driver_report
from utils.score_logger import load_scores, clear_scores

st.set_page_config(layout="wide")

def render_main_ui():
    st.title("LogGen - Otimização de Rotas com Algoritmo Genético")

    # Loader / gerador de instância
    df = show_instance_loader()
    if df is None:
        return
    
    # --- Opção para gerar relatório por IA ---
    generate_llm_report_flag = st.checkbox(
        "Gerar relatório com IA após a execução",
        value=False,
        help="Se marcado, o relatório será gerado automaticamente ao final da execução."
    )
    
    # Valida colunas
    required_columns = {"x", "y", "priority", "demand"}
    if not required_columns.issubset(df.columns):
        st.error(f"CSV inválido. As colunas obrigatórias são: {required_columns}")
        return
    
    st.success("Instância carregada com sucesso.")
    st.dataframe(df.head())

    coords = list(zip(df["x"], df["y"]))
    priorities = df["priority"].tolist()
    demands = df["demand"].tolist() 

    # Sidebar parâmetros
    st.sidebar.header("Parâmetros do Algoritmo")
    n_generations = st.sidebar.slider("Número de gerações", 10, 500, 150)
    pop_size = st.sidebar.slider("Tamanho da população", 10, 200, 60)
    mutation_prob = st.sidebar.slider("Probabilidade de mutação", 0.0, 1.0, 0.2)
    elitism = st.sidebar.slider("Elitismo", 0, 20, 4)
    max_capacity = st.sidebar.number_input("Capacidade máxima por veículo", min_value=1, value=100)
    penalty_weight = st.sidebar.slider("Peso da penalidade por carga", 0.1, 20.0, 3.0)
    n_vehicles = st.sidebar.slider("Número de veículos", 1, 10, 3)
    max_autonomy = st.sidebar.number_input("Autonomia máxima por veículo (km)", min_value=1, value=200)
    autonomy_penalty_weight = st.sidebar.slider("Peso da penalidade por autonomia", 0.1, 20.0, 3.0)

    depot = (0.0, 0.0)

    st.sidebar.header("Balanceamento")
    balance_load_weight = st.sidebar.slider("Peso balanceamento de carga", 0.0, 20.0, 0.0)
    balance_distance_weight = st.sidebar.slider("Peso balanceamento de distância", 0.0, 20.0, 0.0)

    st.sidebar.header("Prioridade mais cedo")
    priority_lateness_weight = st.sidebar.slider("Peso de atraso para prioridade alta", 0.0, 20.0, 0.0)

    st.sidebar.header("Limite de paradas")
    max_stops_per_vehicle = st.sidebar.number_input("Max paradas por veículo", min_value=1, value=10)
    stop_penalty_weight = st.sidebar.slider("Peso da penalidade por paradas", 0.1, 20.0, 5.0)

    # Info instância
    total_demand = sum(demands)
    st.sidebar.markdown("### Informações da Instância")
    st.sidebar.markdown(f"- Demanda total: **{total_demand}**")
    st.sidebar.markdown(f"- Capacidade total disponível: **{max_capacity * n_vehicles}**")

    if len(coords) > n_vehicles * max_stops_per_vehicle:
        st.sidebar.warning("⚠️ Pontos totais maiores que o limite total de paradas. Penalidades serão aplicadas.")


    if total_demand > max_capacity * n_vehicles:
        st.warning(f"⚠️ Demanda total ({total_demand}) excede capacidade total ({max_capacity * n_vehicles}).")
    else:
        st.info(f"Demanda dentro da capacidade ({max_capacity * n_vehicles}).")

    # Cria placeholders para plots e passa callbacks para o serviço
    plot_placeholders, figs_axes = create_plot_placeholders()

    params = {
        "n_generations": n_generations,
        "pop_size": pop_size,
        "mutation_prob": mutation_prob,
        "elitism": elitism,
        "max_capacity": max_capacity,
        "penalty_weight": penalty_weight,
        "n_vehicles": n_vehicles,
        "max_autonomy": max_autonomy,
        "autonomy_penalty_weight": autonomy_penalty_weight,
        "depot": depot,
        "balance_load_weight": balance_load_weight,
        "balance_distance_weight": balance_distance_weight,
        "priority_lateness_weight": priority_lateness_weight,
        "max_stops_per_vehicle": max_stops_per_vehicle,
        "stop_penalty_weight": stop_penalty_weight,
    }

    # Executa serviço que roda o GA e monta relatórios
    try:
        with st.spinner("Executando o algoritmo genético... Gerando relatórios..."):
            result = run_ga_and_build_report(
                coords=coords,
                priorities=priorities,
                demands=demands,
                params=params,
                plot_placeholders=plot_placeholders,
                figs_axes=figs_axes,
            )

        st.subheader("Métricas da Execução")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Distância total", f"{result['total_distance']:.2f}")
            st.metric("Tempo de execução", f"{result['execution_time']:.2f} s")
            st.metric("Convergência em", f"{result['convergence_gen']} gerações")

        with col2:
            if result["brute_force_cost"]:
                st.metric("Custo ótimo (brute force)", f"{result['brute_force_cost']:.2f}")
                st.metric("Gap comparado a solução ótima (%)", f"{result['gap']:.2f} %")
            else:
                st.info("Brute force só disponível para ≤10 pontos.")

        # Resultado contém best_solution, fitness_evolution, df_routes, run_dict, total_distance
        best_solution = result.get("best_solution")
        fitness_evolution = result.get("fitness_evolution")
        df_routes = result.get("df_routes")
        run_dict = result.get("run_dict")
        total_distance = result.get("total_distance")

        st.session_state.update({
            "best_solution": best_solution,
            "fitness_evolution": fitness_evolution,
            "run_dict": run_dict,
        })

        # Exibe tabela resumo por veículo
        st.subheader("Resumo por Veículo")
        st.dataframe(df_routes)

    except Exception as e:
        st.error(f"Erro na execução do algoritmo: {e}")


    # --- Relatório Gerado pela IA (LLM) ---
    if generate_llm_report_flag:
        try:
            with st.spinner("Gerando relatório com a IA..."):
                llm_report = generate_driver_report(st.session_state.get("run_dict", {}))
                st.session_state["llm_report"] = llm_report
            st.success("Relatório da IA gerado com sucesso!")
            with st.expander("Exibir relatório da IA", expanded=False):
                st.markdown(st.session_state["llm_report"])
                buffer = io.BytesIO(st.session_state["llm_report"].encode("utf-8"))
                st.download_button(
                    label="⬇️ Baixar relatório",
                    data=buffer,
                    file_name="relatorio_IA.txt",
                    mime="text/plain",
                    key="download_llm_report_auto",
                )
        except Exception as e:
            st.error(f"Erro ao gerar relatório da IA: {e}")
    else:
        st.info("Geração automática de relatório por IA está desativada.")


    # --- Histórico de Execuções ---
    # Mostra tabela com resultados anteriores e botão para limpar
    st.subheader("Histórico de Execuções")

    # estado local do histórico
    if "score_df" not in st.session_state:
        st.session_state["score_df"] = load_scores()

    placeholder = st.empty()  # local fixo na tela

    with placeholder.container():
        st.dataframe(st.session_state["score_df"])

    # botão para limpar o histórico
    if st.button("Limpar histórico"):
        try:
            clear_scores()
            st.session_state["score_df"] = load_scores()  # recarrega vazio
            placeholder.empty()                           # limpa conteúdo antigo
            with placeholder.container():
                st.dataframe(st.session_state["score_df"])
            st.success("Histórico limpo!")
        except Exception as e:
            st.error(f"Erro ao limpar histórico: {e}")

