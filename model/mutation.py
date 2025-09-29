from __future__ import annotations
from typing import Sequence, List, Tuple
import random

def mutate(solution: Sequence[Tuple[float, float]], mutation_probability: float) -> List[Tuple[float, float]]:
    """
    Aplica mutação simples à solução: troca dois pontos aleatórios com uma certa probabilidade.

    Args:
        solution: Lista de pontos representando uma rota.
        mutation_probability: Probabilidade de realizar a mutação.

    Returns:
        Uma nova solução (lista de pontos) possivelmente mutada.
    """
    sol = list(solution)  # cópia rasa é suficiente

    if len(sol) > 1 and random.random() < mutation_probability:
        # Sorteia duas posições distintas e as inverte
        i, j = sorted(random.sample(range(len(sol)), 2))
        sol[i], sol[j] = sol[j], sol[i]

    return sol
