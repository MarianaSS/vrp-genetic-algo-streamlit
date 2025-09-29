import pandas as pd
import random
import yaml
import os

def generate_instance(config_path="configs/instance_config.yaml", output_path="data/processed/instance.csv"):
    # Carrega parâmetros do YAML
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    n_clients = config["num_clients"]
    seed = config.get("random_seed", 42)
    random.seed(seed)

    # Gerar clientes com coordenadas (x, y), demanda e prioridade
    data = []

    # Adiciona o depósito fixo (id 0)
    data.append({
        "id": 0,
        "x": 0.0,
        "y": 0.0,
        "demand": 0,
        "priority": "normal"
    })

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
    print(f"Instância gerada com sucesso em: {output_path}")

if __name__ == "__main__":
    generate_instance()