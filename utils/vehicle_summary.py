from typing import List, Tuple, Dict
import pandas as pd
from utils.geometry import euclidean_distance

# Define um ponto 2D como tupla de floats
Point = Tuple[float, float]

def generate_vehicle_summary(
    solution: List[List[Point]],
    demand_map: Dict[Point, float],
    depot: Point,
    max_capacity: float,
    max_autonomy: float,
    max_stops_per_vehicle: int
) -> pd.DataFrame:
    """
    Gera um resumo por veículo com base na solução calculada.

    Para cada rota da solução, calcula:
    - número de paradas
    - carga total
    - distância total
    - excesso de capacidade
    - excesso de autonomia
    - excesso de paradas

    Parâmetros:
    - solution: lista de rotas (uma rota por veículo)
    - demand_map: mapa de demanda para cada ponto
    - depot: ponto de origem/destino dos veículos
    - max_capacity: capacidade máxima de carga por veículo
    - max_autonomy: distância máxima permitida por veículo
    - max_stops_per_vehicle: número máximo de paradas permitido por rota

    Retorna:
    - DataFrame com uma linha por veículo e colunas com os indicadores descritos.
    """
    rows = []

    for vidx, route in enumerate(solution, start=1):
        if not route:
            # Caso o veículo não tenha nenhuma parada
            rows.append({
                "veiculo": vidx,
                "paradas": 0,
                "carga_total": 0.0,
                "distancia_total": 0.0,
                "excesso_capacidade": 0.0,
                "excesso_autonomia": 0.0,
                "excesso_paradas": 0,
            })
            continue

        # Distância de ida e volta entre depósito e rota
        dist = euclidean_distance(depot, route[0]) + euclidean_distance(route[-1], depot)

        # Distância entre os pontos da rota
        for i in range(len(route) - 1):
            dist += euclidean_distance(route[i], route[i + 1])

        # Cálculo da carga total da rota
        carga = sum(demand_map.get(tuple(p), 0.0) for p in route)

        # Penalidades por excessos
        excesso_cap = max(0.0, carga - max_capacity)
        excesso_auto = max(0.0, dist - max_autonomy)
        excesso_paradas = max(0, len(route) - max_stops_per_vehicle)

        rows.append({
            "veiculo": vidx,
            "paradas": len(route),
            "carga_total": round(carga, 3),
            "distancia_total": round(dist, 3),
            "excesso_capacidade": round(excesso_cap, 3),
            "excesso_autonomia": round(excesso_auto, 3),
            "excesso_paradas": excesso_paradas,
        })

    return pd.DataFrame(rows)
