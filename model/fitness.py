from __future__ import annotations
from typing import Dict, List, Tuple
import math

Point = Tuple[float, float]

def euclidean_distance(p1: Point, p2: Point) -> float:
    """
    Calcula a distância euclidiana entre dois pontos.
    """
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return (dx * dx + dy * dy) ** 0.5

def _normalize_priority(value: str) -> str:
    """
    Converte a prioridade para o formato padronizado (minúsculo).
    """
    if not isinstance(value, str):
        return "low"
    return value.strip().lower()

def _std(values: List[float]) -> float:
    """
    Calcula o desvio padrão de uma lista de valores.
    """
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / len(values)
    return var ** 0.5

def _calculate_route_metrics(
    route: List[Point],
    depot: Point,
    priority_map: Dict[Point, str],
    demand_map: Dict[Point, float],
    max_capacity: float,
    penalty_weight: float,
    max_autonomy: float,
    autonomy_penalty_weight: float,
    max_stops_per_vehicle: int,
    stop_penalty_weight: float,
    priority_lateness_weight: float,
) -> Tuple[float, float, float]:
    """
    Calcula métricas e penalidades associadas a uma única rota.
    Retorna: (distância total com penalidades, carga total, penalidade de prioridade)
    """
    if not route:
        return 0.0, 0.0, 0.0

    route_distance = euclidean_distance(depot, route[0]) + euclidean_distance(route[-1], depot)
    capacity_used = 0.0
    lateness_penalty = 0.0

    for i, current in enumerate(route):
        nxt = route[i + 1] if i + 1 < len(route) else None

        prio = _normalize_priority(priority_map.get(current, "low"))
        demand = demand_map.get(current, 0.0)
        capacity_used += demand

        weight = {"low": 1.0, "medium": 1.2, "high": 1.5}.get(prio, 1.0)

        if nxt:
            route_distance += euclidean_distance(current, nxt) * weight

        if prio == "high" and priority_lateness_weight > 0.0:
            pos_factor = (i + 1) / max(1, len(route))
            lateness_penalty += pos_factor * priority_lateness_weight

    # Penalidade por excesso de carga
    overload = max(0.0, capacity_used - max_capacity)
    overload_penalty = overload * penalty_weight

    # Penalidade por paradas em excesso
    excess_stops = max(0, len(route) - max_stops_per_vehicle)
    stops_penalty = excess_stops * stop_penalty_weight

    # Penalidade por autonomia excedida
    autonomy_excess = max(0.0, route_distance - max_autonomy)
    autonomy_penalty = autonomy_excess * autonomy_penalty_weight

    total = route_distance + overload_penalty + autonomy_penalty + stops_penalty
    return total, capacity_used, lateness_penalty

def calculate_fitness_multi_vehicle(
    solution: List[List[Point]],
    priority_map: Dict[Point, str],
    demand_map: Dict[Point, float],
    max_capacity: float,
    penalty_weight: float,
    max_autonomy: float = float("inf"),
    autonomy_penalty_weight: float = 10.0,
    depot: Point = (0.0, 0.0),
    balance_load_weight: float = 0.0,
    balance_distance_weight: float = 0.0,
    priority_lateness_weight: float = 0.0,
    max_stops_per_vehicle: int = 10,
    stop_penalty_weight: float = 5.0,
) -> float:
    """
    Calcula a aptidão (fitness) de uma solução multi-veículo,
    considerando distância total e penalidades logísticas.
    """
    total_distance = 0.0
    route_loads: List[float] = []
    route_distances: List[float] = []
    total_lateness_penalty = 0.0

    for route in solution:
        distance, load, lateness = _calculate_route_metrics(
            route=route,
            depot=depot,
            priority_map=priority_map,
            demand_map=demand_map,
            max_capacity=max_capacity,
            penalty_weight=penalty_weight,
            max_autonomy=max_autonomy,
            autonomy_penalty_weight=autonomy_penalty_weight,
            max_stops_per_vehicle=max_stops_per_vehicle,
            stop_penalty_weight=stop_penalty_weight,
            priority_lateness_weight=priority_lateness_weight,
        )
        total_distance += distance
        route_loads.append(load)
        route_distances.append(distance)
        total_lateness_penalty += lateness

    # Penalidade por desequilíbrio de carga entre veículos
    if balance_load_weight > 0.0:
        total_distance += _std(route_loads) * balance_load_weight

    # Penalidade por desequilíbrio de distância entre veículos
    if balance_distance_weight > 0.0:
        total_distance += _std(route_distances) * balance_distance_weight

    # Penalidade total por entrega tardia de prioridades altas
    total_distance += total_lateness_penalty

    return total_distance
