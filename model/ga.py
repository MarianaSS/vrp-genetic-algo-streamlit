from __future__ import annotations
from typing import Dict, List, Sequence, Tuple, Callable, Optional
import random

from model.fitness import calculate_fitness_multi_vehicle
from model.crossover import order_crossover
from model.mutation import mutate

Point = Tuple[float, float]
OnGenCb = Callable[[int, Sequence[List[Point]], float, List[float]], None]

def run_ga(
    coords: Sequence[Point],
    priorities: Sequence[str],
    demands: Sequence[float],
    n_generations: int,
    pop_size: int,
    mutation_prob: float,
    elitism: int,
    max_capacity: float,
    penalty_weight: float,
    n_vehicles: int = 3,
    max_autonomy: float = float("inf"),
    autonomy_penalty_weight: float = 10.0,
    depot: Point = (0.0, 0.0),
    balance_load_weight: float = 0.0,
    balance_distance_weight: float = 0.0,
    priority_lateness_weight: float = 0.0,
    max_stops_per_vehicle: int = 10,
    stop_penalty_weight: float = 5.0,
    on_generation: Optional[OnGenCb] = None,
) -> Tuple[List[List[Point]], List[float]]:
    """
    Executa o algoritmo genético para resolver o problema de roteamento com múltiplos veículos.
    """

    random.seed(42)

    # Mapeia coordenadas para prioridade e demanda
    priority_map: Dict[Point, str] = {tuple(c): p for c, p in zip(coords, priorities)}
    demand_map: Dict[Point, float] = {tuple(c): float(d) for c, d in zip(coords, demands)}
    coords_list = list(coords)

    # Gera população inicial
    population = [generate_individual(coords_list, demand_map, max_capacity, n_vehicles) for _ in range(pop_size)]
    best_solution: Optional[List[List[Point]]] = None
    fitness_evolution: List[float] = []

    for generation in range(n_generations):
        # Avalia todos os indivíduos
        fitnesses = [
            calculate_fitness_multi_vehicle(
                solution=ind,
                priority_map=priority_map,
                demand_map=demand_map,
                max_capacity=max_capacity,
                penalty_weight=penalty_weight,
                max_autonomy=max_autonomy,
                autonomy_penalty_weight=autonomy_penalty_weight,
                depot=depot,
                balance_load_weight=balance_load_weight,
                balance_distance_weight=balance_distance_weight,
                priority_lateness_weight=priority_lateness_weight,
                max_stops_per_vehicle=max_stops_per_vehicle,
                stop_penalty_weight=stop_penalty_weight,
            )
            for ind in population
        ]

        # Ordena população por fitness crescente
        ranked = sorted(zip(population, fitnesses), key=lambda x: x[1])
        population = [p for p, _ in ranked]
        fitnesses = [f for _, f in ranked]

        # Salva o melhor da geração
        best_solution = population[0]
        best_fitness = fitnesses[0]
        fitness_evolution.append(best_fitness)

        if on_generation:
            on_generation(generation, best_solution, best_fitness, fitness_evolution)

        # Gera nova população com elitismo + reprodução
        population = evolve_population(population, mutation_prob, pop_size, elitism)

    return best_solution or [], fitness_evolution

def generate_individual(
    coords: List[Point],
    demand_map: Dict[Point, float],
    max_capacity: float,
    n_vehicles: int
) -> List[List[Point]]:
    """
    Gera uma solução inicial aleatória respeitando a capacidade dos veículos.
    """
    shuffled = random.sample(coords, len(coords))
    routes = [[] for _ in range(n_vehicles)]
    capacities = [0.0] * n_vehicles

    for point in shuffled:
        demand = demand_map.get(point, 0.0)
        placed = False

        for i in range(n_vehicles):
            if capacities[i] + demand <= max_capacity:
                routes[i].append(point)
                capacities[i] += demand
                placed = True
                break

        if not placed:
            # Se nenhum veículo puder atender, aloca no menos carregado
            j = min(range(n_vehicles), key=lambda k: capacities[k])
            routes[j].append(point)
            capacities[j] += demand

    return routes

def evolve_population(
    population: List[List[List[Point]]],
    mutation_prob: float,
    pop_size: int,
    elitism: int
) -> List[List[List[Point]]]:
    """
    Evolui a população aplicando elitismo, cruzamento e mutação.
    """
    elites = population[:max(0, elitism)]
    new_population = list(elites)

    while len(new_population) < pop_size:
        k = min(10, len(population))
        parent1, parent2 = random.sample(population[:k], 2)
        child = crossover_multi_vehicle(parent1, parent2)
        child = mutate_multi_vehicle(child, mutation_prob)
        new_population.append(child)

    return new_population

def crossover_multi_vehicle(
    p1: List[List[Point]],
    p2: List[List[Point]]
) -> List[List[Point]]:
    """
    Aplica crossover entre dois indivíduos multi-veículo.
    """
    flat1 = [c for route in p1 for c in route]
    flat2 = [c for route in p2 for c in route]
    child_flat = order_crossover(flat1, flat2)
    return repartition(child_flat, len(p1))

def mutate_multi_vehicle(
    solution: List[List[Point]],
    mutation_probability: float
) -> List[List[Point]]:
    """
    Aplica mutação a uma solução multi-veículo.
    """
    flat = [p for route in solution for p in route]
    mutated = mutate(flat, mutation_probability)
    return repartition(mutated, len(solution))

def repartition(flat_list: List[Point], n_parts: int) -> List[List[Point]]:
    """
    Reparticiona uma lista de pontos linear em várias rotas.
    """
    if n_parts <= 0:
        return [flat_list]
    avg = len(flat_list) // n_parts
    extra = len(flat_list) % n_parts
    result = []
    idx = 0
    for i in range(n_parts):
        count = avg + (1 if i < extra else 0)
        result.append(flat_list[idx:idx + count])
        idx += count
    return result
