import os
import pandas as pd

# Nome padrão do arquivo CSV onde os resultados são salvos
_SCORE_FILE = "score_log.csv"

# Lista padrão de colunas utilizadas no CSV
_COLUMNS = [
    "execucao",
    "melhor_distancia",
    "n_generations",
    "pop_size",
    "mutation_prob",
    "elitism",
    "max_capacity",
    "penalty_weight",
    "n_vehicles",
    "max_autonomy",
    "autonomy_penalty_weight",
    "depot_x",
    "depot_y",
    "balance_load_weight",
    "balance_distance_weight",
    "priority_lateness_weight",
    "max_stops_per_vehicle",
    "stop_penalty_weight"
]

def append_score(
    score: float,
    n_generations: int,
    pop_size: int,
    mutation_prob: float,
    elitism: int,
    max_capacity: float,
    penalty_weight: float,
    n_vehicles: int,
    max_autonomy: float,
    autonomy_penalty_weight: float,
    depot_x: float,
    depot_y: float,
    balance_load_weight: float,
    balance_distance_weight: float,
    priority_lateness_weight: float,
    max_stops_per_vehicle: int,
    stop_penalty_weight: float
) -> None:
    """
    Adiciona uma nova linha com os parâmetros da execução atual no arquivo de log de resultados.
    Cria o arquivo se ele ainda não existir.
    """

    # Verifica se o arquivo já existe. Se não, cria um novo DataFrame vazio
    if not os.path.exists(_SCORE_FILE):
        df = pd.DataFrame(columns=_COLUMNS)
    else:
        df = pd.read_csv(_SCORE_FILE)

        # Garante que todas as colunas necessárias estejam presentes
        missing_cols = set(_COLUMNS) - set(df.columns)
        for col in missing_cols:
            df[col] = None
        df = df[_COLUMNS]  # Reordena colunas se necessário

    # Número da execução atual (incremental)
    nova_execucao = len(df) + 1

    # Adiciona nova linha com os parâmetros fornecidos
    df.loc[len(df)] = [
        nova_execucao,
        float(score),
        n_generations,
        pop_size,
        mutation_prob,
        elitism,
        max_capacity,
        penalty_weight,
        n_vehicles,
        max_autonomy,
        autonomy_penalty_weight,
        depot_x,
        depot_y,
        balance_load_weight,
        balance_distance_weight,
        priority_lateness_weight,
        max_stops_per_vehicle,
        stop_penalty_weight
    ]

    # Salva o DataFrame atualizado no CSV
    df.to_csv(_SCORE_FILE, index=False)

def load_scores() -> pd.DataFrame:
    """
    Carrega o arquivo de resultados em um DataFrame. Se não existir, retorna estrutura vazia.
    """
    if not os.path.exists(_SCORE_FILE):
        return pd.DataFrame(columns=_COLUMNS)
    return pd.read_csv(_SCORE_FILE)

def clear_scores() -> None:
    """
    Remove o arquivo de resultados, se existir.
    """
    if os.path.exists(_SCORE_FILE):
        os.remove(_SCORE_FILE)
