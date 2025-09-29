from __future__ import annotations
from typing import Sequence, Tuple, List
import random

def order_crossover(
    parent1: Sequence[Tuple[float, float]],
    parent2: Sequence[Tuple[float, float]]
) -> List[Tuple[float, float]]:
    """
    Operador de cruzamento por ordem (Order Crossover - OX).

    Preserva a ordem relativa de parte dos genes de um dos pais e
    completa o restante com os genes do outro pai, mantendo a viabilidade
    de soluções de permutação.

    Args:
        parent1: Primeiro pai (sequência de pontos)
        parent2: Segundo pai (sequência de pontos)

    Returns:
        Uma nova solução (filho) que combina características dos dois pais.
    """
    assert len(parent1) == len(parent2) > 2, "Pais devem ter mesmo tamanho > 2"
    length = len(parent1)

    # Sorteia uma sublista contínua do primeiro pai
    start, end = sorted(random.sample(range(length), 2))
    slice_from_p1 = parent1[start:end]

    # Pega os genes restantes do segundo pai que não estão na fatia
    remaining_genes = [gene for gene in parent2 if gene not in slice_from_p1]

    # Monta o filho com:
    # - prefixo do segundo pai
    # - fatia copiada do primeiro pai
    # - sufixo do segundo pai
    child = remaining_genes[:start] + list(slice_from_p1) + remaining_genes[start:]

    return child

