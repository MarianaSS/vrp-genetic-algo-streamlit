from generate_instance import generate_instance
from validate_instance import validate_instance

# Caminhos padrão
config_path = "configs/instance_config.yaml"
output_path = "data/processed/instance.csv"

# Geração
generate_instance(config_path=config_path, output_path=output_path)

# Validação
resultado = validate_instance(output_path)
print("Validação:", resultado)