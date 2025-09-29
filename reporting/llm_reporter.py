from typing import Dict, Any, List
from utils.llm_client import get_client

SYSTEM_INSTRUCTIONS = (
    "Você é um assistente de logística. Gere: "
    "1) instruções para motoristas, "
    "2) um resumo executivo, e "
    "3) sugestões de melhoria com base nos dados fornecidos."
)

def _call_llm(prompt: str, model: str = "gpt-4o") -> str:
    client = get_client()
    response = client.responses.create(
        model=model,
        instructions=SYSTEM_INSTRUCTIONS,
        input=prompt
    )
    return response.output_text

def build_prompt_from_run(run: Dict[str, Any]) -> str:
    lines = []
    lines.append(f"Distância total: {run['distancia_total']:.2f} km")
    lines.append("")
    for v in run["veiculos"]:
        lines.append(f"Veículo {v['id']}:")
        lines.append(f"- Distância: {v['distancia']:.2f} km")
        lines.append(f"- Carga: {v['carga']}/{v['capacidade']}")
        lines.append(f"- Paradas: {', '.join(map(str, v['paradas']))}")
        if v.get("excessos"):
            lines.append(f"- Excessos: {', '.join(v['excessos'])}")
        lines.append("")
    return "\n".join(lines)

def generate_driver_report(run: Dict[str, Any], model: str = "gpt-4o") -> str:
    prompt = build_prompt_from_run(run)
    return _call_llm(prompt, model)
