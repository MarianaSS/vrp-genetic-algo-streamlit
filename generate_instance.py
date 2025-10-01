import pandas as pd
import random
import yaml
import os

def generate_instance(
    config_path="configs/instance_config.yaml",
    output_path="data/processed/instance.csv",
    n_points=None
):
    """
    Gera uma instância para o problema VRP/TSP.

    Args:
        config_path (str): caminho para o arquivo YAML (usado como fallback).
        output_path (str): caminho para salvar o CSV.
        n_points (int | None): número de clientes (excluindo o depósito). 
                               Se None, usa valor do YAML.
    """
    # Carrega parâmetros do YAML
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Se usuário não informou n_points, usa o YAML
    if n_points is None:
        n_clients = config["num_clients"]
    else:
        n_clients = min(n_points, 50)  # segurança: máximo 50

    seed = config.get("random_seed", 42)
    random.seed(seed)

    data = []

    # Adiciona o depósito fixo (id 0)
    data.append({
        "id": 0,
        "x": 0.0,
        "y": 0.0,
        "demand": 0,
        "priority": "normal"
    })

    # Gerar clientes
    for i in range(1, n_clients + 1):
        x = round(random.uniform(0, 100), 2)
        y = round(random.uniform(0, 100), 2)
        demand = random.randint(1, 20)
        priority = random.choice(["alta", "normal", "baixa"])
        data.append({
            "id": i,
            "x": x,
            "y": y,
            "demand": demand,
            "priority": priority
        })

    df = pd.DataFrame(data)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Instância com {n_clients} pontos gerada em: {output_path}")

    return df

if __name__ == "__main__":
    generate_instance()