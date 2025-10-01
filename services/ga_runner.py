"""
Serviço que executa o algoritmo genético e gera o relatório.
Exporta run_ga_and_build_report que encapsula a lógica pesada.
"""
from model.ga import run_ga
from utils.geometry import euclidean_distance
from utils.vehicle_summary import generate_vehicle_summary
from reporting.llm_reporter import generate_driver_report
from utils.score_logger import append_score
import time
import itertools
from utils.geometry import euclidean_distance

def brute_force_tsp(coords, depot=(0.0, 0.0)):
    """Resolve TSP com brute force para instâncias pequenas (<=10 pontos)."""
    if len(coords) > 10:
        return None, None
    best_cost = float("inf")
    best_route = None
    for perm in itertools.permutations(coords):
        dist = euclidean_distance(depot, perm[0])
        for a, b in zip(perm, perm[1:]):
            dist += euclidean_distance(a, b)
        dist += euclidean_distance(perm[-1], depot)
        if dist < best_cost:
            best_cost = dist
            best_route = perm
    return best_cost, best_route

def run_ga_and_build_report(coords, priorities, demands, params, plot_placeholders, figs_axes):
    """
    Executa run_ga com callback que atualiza os plots. Retorna um dict com os resultados processados.
    - coords, priorities, demands: dados da instância
    - params: dicionário com parâmetros do algoritmo
    - plot_placeholders: {'p1': placeholder1, 'p2': placeholder2}
    - figs_axes: (fig1, ax1, fig2, ax2)
    """
    start = time.time()
    fig1, ax1, fig2, ax2 = figs_axes
    plot_p1 = plot_placeholders.get("p1")
    plot_p2 = plot_placeholders.get("p2")

    depot = params.get("depot", (0.0, 0.0))

    def on_generation(generation, best_solution, best_score, history):
        if not best_solution:
            return
    
        # desenha rota
        from ui.plot_utils import plot_solution
        plot_solution(ax1, best_solution, depot)
        ax1.set_title(f"Melhor rota - Geração {generation}")
        plot_p1.pyplot(fig1, clear_figure=False)

        # evolução do fitness
        ax2.clear()
        ax2.plot(history)
        ax2.set_title("Evolução do Fitness")
        ax2.set_xlabel("Geração")
        ax2.set_ylabel("Custo (distância + penalidades)")
        plot_p2.pyplot(fig2, clear_figure=False)

    # Chama run_ga
    best_solution, fitness_evolution = run_ga(
        coords=coords,
        priorities=priorities,
        demands=demands,
        n_generations=params["n_generations"],
        pop_size=params["pop_size"],
        mutation_prob=params["mutation_prob"],
        elitism=params["elitism"],
        max_capacity=params["max_capacity"],
        penalty_weight=params["penalty_weight"],
        n_vehicles=params["n_vehicles"],
        max_autonomy=params["max_autonomy"],
        autonomy_penalty_weight=params["autonomy_penalty_weight"],
        depot=params["depot"],
        balance_load_weight=params["balance_load_weight"],
        balance_distance_weight=params["balance_distance_weight"],
        priority_lateness_weight=params["priority_lateness_weight"],
        max_stops_per_vehicle=params["max_stops_per_vehicle"],
        stop_penalty_weight=params["stop_penalty_weight"],
        on_generation=on_generation,
    )

    execution_time = time.time() - start

    # calcula total_distance
    def route_distance(route, depot):
            if not route:
                return 0.0
            dist = euclidean_distance(depot, route[0])
            for a, b in zip(route, route[1:]):
                dist += euclidean_distance(a, b)
            dist += euclidean_distance(route[-1], depot)
            return dist
        
    total_distance = sum(route_distance(r, params["depot"]) for r in best_solution)
    demand_map = {tuple(c): float(d) for c, d in zip(coords, demands)}

    df_routes = generate_vehicle_summary(
        solution=best_solution,
        demand_map=demand_map,
        depot=params["depot"],
        max_capacity=params["max_capacity"],
        max_autonomy=params["max_autonomy"],
        max_stops_per_vehicle=params["max_stops_per_vehicle"],
    )

    # monta run_dict para LLM
    run_dict = {"distancia_total": float(total_distance), "veiculos": []}
    for idx, row in df_routes.iterrows():
        run_dict["veiculos"].append({
            "id": int(row["veiculo"]),
            "distancia": float(row["distancia_total"]),
            "carga": float(row["carga_total"]),
            "capacidade": float(params["max_capacity"]),
            "paradas": [f"P{idx}" for idx in range(int(row["paradas"]))],
            "excessos": [
                *( ["capacidade"] if row["excesso_capacidade"] > 0 else [] ),
                *( ["autonomia"] if row["excesso_autonomia"] > 0 else [] ),
            ],
        })

    # gera relatório
    try:
        relatorio = generate_driver_report(run_dict)
    except Exception:
        relatorio = ""

    # persiste score
    try:
        append_score(
            score=fitness_evolution[-1] if fitness_evolution else float('inf'),
            n_generations=params["n_generations"],
            pop_size=params["pop_size"],
            mutation_prob=params["mutation_prob"],
            elitism=params["elitism"],
            max_capacity=params["max_capacity"],
            penalty_weight=params["penalty_weight"],
            n_vehicles=params["n_vehicles"],
            max_autonomy=params["max_autonomy"],
            autonomy_penalty_weight=params["autonomy_penalty_weight"],
            depot_x=params["depot"][0],
            depot_y=params["depot"][1],
            balance_load_weight=params["balance_load_weight"],
            balance_distance_weight=params["balance_distance_weight"],
            priority_lateness_weight=params["priority_lateness_weight"],
            max_stops_per_vehicle=params["max_stops_per_vehicle"],
            stop_penalty_weight=params["stop_penalty_weight"],
        )
    except Exception:
        pass

    # calcula em qual geração houve convergência (primeira vez que o melhor fitness final apareceu)
    convergence_gen = len(fitness_evolution)
    if fitness_evolution:
        best_final = fitness_evolution[-1]
        for i in range(1, len(fitness_evolution)):
            if fitness_evolution[i] == best_final:
                convergence_gen = i
                break

    # calcula gap entre a solução e brute force e a ga
    brute_force_cost, _ = brute_force_tsp(coords)
    gap = None
    if brute_force_cost:
        gap = 100 * (total_distance - brute_force_cost) / brute_force_cost

    return {
        "best_solution": best_solution,
        "fitness_evolution": fitness_evolution,
        "df_routes": df_routes,
        "run_dict": run_dict,
        "total_distance": total_distance,
        "relatorio": relatorio,
        "execution_time": execution_time,
        "convergence_gen": convergence_gen,
        "brute_force_cost": brute_force_cost,
        "gap": gap,
    }
