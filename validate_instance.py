import pandas as pd

def validate_instance(csv_path):
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        return f"Erro ao ler o arquivo: {e}"

    required_columns = {"id", "x", "y", "demand", "priority"}
    if not required_columns.issubset(df.columns):
        return f"Colunas ausentes. Esperadas: {required_columns}"

    if df.iloc[0]["id"] != 0:
        return "O primeiro ponto (depósito) deve ter id = 0."

    if df.iloc[0]["demand"] != 0:
        return "O depósito deve ter demanda igual a 0."

    if not pd.api.types.is_numeric_dtype(df["x"]) or not pd.api.types.is_numeric_dtype(df["y"]):
        return "Colunas 'x' e 'y' devem ser numéricas."

    if df["demand"].lt(0).any():
        return "Demandas negativas encontradas."

    if df["priority"].isnull().any():
        return "Há valores de prioridade ausentes."

    return "Instância válida ✅"