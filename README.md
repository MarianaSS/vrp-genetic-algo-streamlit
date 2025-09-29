# Algoritmo Genético para TSP com Demanda e Prioridade

- TSP com prioridades (`low|medium|high`) e demanda por nó.
- Penalidade linear por excesso de capacidade total.
- UI em Streamlit. GA reprodutível via `seed`.

## Uso rápido

```bash
pip install -r requirements.txt
streamlit run tsp_ga/main.py
```

### CSV de entrada
Colunas obrigatórias (case-insensitive): `id,x,y,demand,priority`.

### Parâmetros principais
- `max_capacity`: limite de soma das demandas.
- `penalty_weight`: custo por unidade acima da capacidade.
- `elitism`: jogadores mantidos a cada geração.
- `mutation_prob`: probabilidade de mutação.
- `seed`: reprodutibilidade.
