from typing import Tuple

# Define um tipo para representar um ponto bidimensional (x, y)
Point = Tuple[float, float]

def euclidean_distance(p1: Point, p2: Point) -> float:
    """
    Calcula a distância euclidiana entre dois pontos em 2D.

    Fórmula: sqrt((x2 - x1)^2 + (y2 - y1)^2)

    Parâmetros:
    - p1: primeiro ponto (x, y)
    - p2: segundo ponto (x, y)

    Retorna:
    - Distância em linha reta entre os dois pontos
    """
    dx = p1[0] - p2[0]  # diferença entre as coordenadas x
    dy = p1[1] - p2[1]  # diferença entre as coordenadas y
    return (dx * dx + dy * dy) ** 0.5  # raiz quadrada da soma dos quadrados
