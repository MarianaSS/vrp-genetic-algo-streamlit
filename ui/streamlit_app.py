import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from model.ga import run_ga
from utils.score_logger import append_score, load_scores, clear_scores
from ui.plot_utils import plot_solution
from reporting.llm_reporter import generate_driver_report
from utils.vehicle_summary import generate_vehicle_summary
from utils.geometry import euclidean_distance
from generate_instance import generate_instance
from validate_instance import validate_instance

def main():
    st.title("Otimização de Rotas com Algoritmo Genético (VRP)")

    # Botão para limpar histórico
    if st.button("🧹 Limpar histórico"):
        try:
            clear_scores()
            st.success("Histórico limpo!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao limpar histórico: {e}")

    st.title("Gerador de Instância ou Upload de arquivo (VRP)")

    config_path = "configs/instance_config.yaml"
    output_path = "data/processed/instance.csv"

    # Opção 1 – Gerar instância sintética
    if st.button("🔄 Gerar nova instância"):
        try:
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

    # Opção 2 – Upload manual
    uploaded_file = st.file_uploader("Ou carregue um arquivo CSV manualmente:", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.session_state["df"] = df

    if "df" in st.session_state:
        df = st.session_state["df"]

        required_columns = {"x", "y", "priority", "demand"}
        if not required_columns.issubset(df.columns):
            st.error(f"CSV inválido. As colunas obrigatórias são: {required_columns}")
            return

        st.success("Instância carregada com sucesso ✅")
        st.dataframe(df.head())

        coords = list(zip(df["x"], df["y"]))
        priorities = df["priority"].tolist()
        demands = df["demand"].tolist()

        # Sidebar com parâmetros configuráveis
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

        # Informações gerais
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

        # Gráficos
        plot_placeholder1 = st.empty()
        plot_placeholder2 = st.empty()
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        fig2, ax2 = plt.subplots(figsize=(6, 4))

        def on_generation(generation, best_solution, best_score, history):
            """
            Callback executado a cada geração. Atualiza os gráficos com as melhores rotas e evolução do fitness.
            """
            if not best_solution:
                return
            plot_solution(ax1, best_solution, depot)
            ax1.set_title(f"Melhor rota - Geração {generation}")
            plot_placeholder1.pyplot(fig1, clear_figure=False)

            ax2.clear()
            ax2.plot(history)
            ax2.set_title("Evolução do Fitness")
            ax2.set_xlabel("Geração")
            ax2.set_ylabel("Custo (distância + penalidades)")
            plot_placeholder2.pyplot(fig2, clear_figure=False)

        # Executa algoritmo genético
        best_solution, fitness_evolution = run_ga(
            coords=coords,
            priorities=priorities,
            demands=demands,
            n_generations=n_generations,
            pop_size=pop_size,
            mutation_prob=mutation_prob,
            elitism=elitism,
            max_capacity=max_capacity,
            penalty_weight=penalty_weight,
            n_vehicles=n_vehicles,
            max_autonomy=max_autonomy,
            autonomy_penalty_weight=autonomy_penalty_weight,
            depot=depot,
            balance_load_weight=balance_load_weight,
            balance_distance_weight=balance_distance_weight,
            priority_lateness_weight=priority_lateness_weight,
            max_stops_per_vehicle=max_stops_per_vehicle,
            stop_penalty_weight=stop_penalty_weight,
            on_generation=on_generation
        )

        best_score = fitness_evolution[-1] if fitness_evolution else float("inf")

        # Crie o demand_map
        demand_map = {tuple(c): float(d) for c, d in zip(coords, demands)}

        # Calcule a distância total
        def route_distance(route, depot):
            if not route: return 0.0
            dist = euclidean_distance(depot, route[0])
            for a, b in zip(route, route[1:]):
                dist += euclidean_distance(a, b)
            dist += euclidean_distance(route[-1], depot)
            return dist

        total_distance = sum(route_distance(r, depot) for r in best_solution)

        # Gera resumo por veículo
        df_sum = generate_vehicle_summary(
            solution=best_solution,
            demand_map=demand_map,
            depot=depot,
            max_capacity=max_capacity,
            max_autonomy=max_autonomy,
            max_stops_per_vehicle=max_stops_per_vehicle
        )

        # Constrói o run_dict para a LLM
        run_dict = {
            "distancia_total": float(total_distance),
            "veiculos": []
        }

        for idx, row in df_sum.iterrows():
            run_dict["veiculos"].append({
                "id": int(row["veiculo"]),
                "distancia": float(row["distancia_total"]),
                "carga": float(row["carga_total"]),
                "capacidade": float(max_capacity),
                "paradas": [f"P{idx}" for idx in range(int(row["paradas"]))],  # ou IDs reais, se tiver
                "excessos": [
                    *(["capacidade"] if row["excesso_capacidade"] > 0 else []),
                    *(["autonomia"] if row["excesso_autonomia"] > 0 else []),
                ]
            })

        # Salva os resultados no session_state
        st.session_state["best_solution"] = best_solution
        st.session_state["fitness_evolution"] = fitness_evolution
        st.session_state["run_dict"] = run_dict

        # Gera o relatório automaticamente
        st.subheader("Relatório com LLM")
        try:
            relatorio = generate_driver_report(run_dict)
            st.markdown(relatorio)
            st.download_button(
                "Baixar relatório em Markdown",
                relatorio.encode("utf-8"),
                file_name="relatorio_llm.md",
                key="btn_download_relatorio"
            )
        except Exception as e:
            st.error(f"Erro ao gerar relatório: {e}")


        # Salva resultado no histórico
        append_score(
            score=best_score,
            n_generations=n_generations,
            pop_size=pop_size,
            mutation_prob=mutation_prob,
            elitism=elitism,
            max_capacity=max_capacity,
            penalty_weight=penalty_weight,
            n_vehicles=n_vehicles,
            max_autonomy=max_autonomy,
            autonomy_penalty_weight=autonomy_penalty_weight,
            depot_x=depot[0],
            depot_y=depot[1],
            balance_load_weight=balance_load_weight,
            balance_distance_weight=balance_distance_weight,
            priority_lateness_weight=priority_lateness_weight,
            max_stops_per_vehicle=max_stops_per_vehicle,
            stop_penalty_weight=stop_penalty_weight
        )

        # Tabela resumo por veículo
        st.subheader("Resumo por Veículo")
        demand_map = {tuple(c): float(d) for c, d in zip(coords, demands)}
        df_routes = generate_vehicle_summary(
            solution=best_solution,
            demand_map=demand_map,
            depot=depot,
            max_capacity=max_capacity,
            max_autonomy=max_autonomy,
            max_stops_per_vehicle=max_stops_per_vehicle
        )
        st.dataframe(df_routes)

        # Histórico de execuções
        st.subheader("Histórico de Execuções")
        score_df = load_scores()
        st.dataframe(score_df)
