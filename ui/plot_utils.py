import matplotlib.pyplot as plt
import matplotlib.cm as cm
from typing import List, Tuple

Point = Tuple[float, float]

def plot_solution(ax: plt.Axes, solution: List[List[Point]], depot: Point = (0.0, 0.0)) -> None:
    """
    Plota graficamente as rotas dos veículos a partir da solução fornecida.

    Cada rota é representada como uma linha que parte do depósito, passa pelos pontos atribuídos ao veículo,
    e retorna ao depósito. Cores distintas são usadas para cada veículo.

    Parâmetros:
    - ax: objeto matplotlib Axes onde a figura será desenhada.
    - solution: lista de rotas, onde cada rota é uma lista de pontos (x, y).
    - depot: ponto central (x, y) de onde os veículos partem e retornam. Default: (0.0, 0.0)
    """
    ax.clear()

    # Seleciona colormap com até 10 cores distintas
    colors = cm.get_cmap('tab10', max(1, len(solution)))

    # Plota o depósito como quadrado
    ax.scatter([depot[0]], [depot[1]], marker='s', s=80, label="Depósito")

    for i, route in enumerate(solution):
        if not route:
            continue  # ignora rotas vazias

        # Constrói lista de coordenadas da rota: depósito -> pontos -> depósito
        xs = [depot[0], route[0][0]] + [p[0] for p in route] + [route[-1][0], depot[0]]
        ys = [depot[1], route[0][1]] + [p[1] for p in route] + [route[-1][1], depot[1]]

        # Plota linha conectando os pontos da rota com marcador circular
        ax.plot(xs, ys, 'o-', label=f"Veículo {i+1}", color=colors(i))

    # Mostra legenda com rótulo para cada veículo
    ax.legend()
    ax.set_title("Rotas por Veículo (com Depósito)")
