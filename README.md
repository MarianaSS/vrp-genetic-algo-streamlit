# 🚚 VRP Solver com Algoritmo Genético + IA (Streamlit)

Este projeto resolve o problema de roteamento de veículos com múltiplas restrições (VRP) usando um algoritmo genético customizado, visualização interativa com Streamlit, e integração com LLMs (GPT-4o) para geração de relatórios automatizados.

---

## 🔧 Funcionalidades

- Geração de instâncias sintéticas com parâmetros configuráveis
- Resolução do VRP com:
  - Capacidade de carga
  - Autonomia
  - Número de veículos
  - Prioridade de entrega
  - Penalidades personalizadas
- Visualização das rotas otimizadas
- Análise de convergência e desempenho
- Comparação com brute-force para instâncias pequenas
- Relatórios automáticos via OpenAI LLM (GPT-4o)
- Histórico de execuções e exportação de resultados

---

## 📁 Estrutura do projeto

```
├── configs/             # Arquivos .yaml para geração de instâncias
├── data/processed/      # Instâncias CSV geradas
├── model/               # Algoritmo genético e operadores
├── ui/                  # Componentes de visualização e interação
├── utils/               # Métricas, histórico, geometria, validação
├── reporting/           # Integração com LLM para relatórios
├── main_app.py          # Aplicação principal Streamlit
├── requirements.txt     # Dependências do projeto
└── README.md            # Este arquivo
```

---

## ▶️ Como executar localmente

1. Clone o repositório:

```bash
git clone git@github.com:MarianaSS/vrp-genetic-algo-streamlit.git
cd vrp-genetic-algo-streamlit
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Configure sua chave OpenAI (opcional para IA):

```bash
export OPENAI_API_KEY=sk-...  # ou configure em .env
```

4. Execute o app:

```bash
streamlit run main_app.py
```

---

## ☁️ Deploy online

---

## 🧠 Licença

MIT © [MarianaSS](https://github.com/MarianaSS)