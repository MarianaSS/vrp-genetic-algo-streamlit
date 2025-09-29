from __future__ import annotations
from typing import Dict, List, Sequence, Tuple
from model.fitness import calculate_fitness

Point = Tuple[float, float]

def sort_population(
    population: Sequence[Sequence[Point]],
    priority_map: Dict[Point, str],
    demand_map: Dict[Point, float],
    max_capacity: float,
    penalty_weight: float
) -> Tuple[List[Sequence[Point]], List[float]]:
    """
    Avalia e ordena a população com base no fitness (distância + penalidades).

    Args:
        population: Lista de indivíduos (rotas completas).
        priority_map: Dicionário com prioridade de cada ponto.
        demand_map: Dicionário com demanda de cada ponto.
        max_capacity: Capacidade máxima por rota.
        penalty_weight: Peso da penalidade por excesso de carga.

    Returns:
        Uma tupla contendo:
        - população ordenada do melhor para o pior
        - lista dos fitness correspondentes
    """
    # Avalia todos os indivíduos
    fitnesses = [
        calculate_fitness(ind, priority_map, demand_map, max_capacity, penalty_weight)
        for ind in population
    ]

    # Ordena os pares (indivíduo, fitness) pelo valor do fitness
    pairs = sorted(zip(population, fitnesses), key=lambda x: x[1])

    sorted_population = [p for p, _ in pairs]
    sorted_fitnesses = [f for _, f in pairs]

    return sorted_population, sorted_fitnesses
