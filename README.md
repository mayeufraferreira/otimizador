# 🌍 Otimizador de Workloads Multi-Objetivo

Sistema inteligente para alocação de workloads em datacenters, otimizando múltiplas métricas: **latência**, **sustentabilidade** (energia renovável) e **custo**.

## 📋 Descrição

Este projeto implementa um motor de decisão que seleciona a melhor região (datacenter) para executar workloads, considerando diferentes modos operacionais e priorizando diferentes métricas conforme a necessidade.

## 🏗️ Estrutura do Projeto

```
otimizador/
├── src/
│   ├── models/              # Modelos de dados
│   │   ├── region.py        # Modelo de região/datacenter
│   │   └── workload.py      # Modelo de carga de trabalho
│   ├── algorithms/          # Lógica de otimização
│   │   ├── constraints.py   # Validação de constraints obrigatórias
│   │   ├── scorer.py        # Cálculo de scores das métricas
│   │   └── decision_engine.py  # Motor de decisão principal
│   └── tests/               # Testes e experimentos
│       ├── experiments_scenarios.py  # Cenários de teste
│       └── run_experiments.py        # Executor de experimentos
├── simulator/               # Geração e simulação de dados
│   ├── data_generator.py    # Gera regiões e workloads aleatórios
│   └── orchestrator.py      # Orquestra as simulações
├── analysis/                # Análise de resultados
│   └── analysis.py          # Ferramentas de análise
├── results/                 # Resultados das simulações
└── requirements.txt         # Dependências do projeto
```

## 🎯 Métricas Otimizadas

1. **Latência** - Tempo de resposta entre usuário e datacenter
2. **Sustentabilidade** - Porcentagem de energia renovável e emissões de carbono
3. **Custo** - Custo de energia por kWh

## 🔧 Modos Operacionais

O sistema suporta 4 modos operacionais com diferentes pesos para as métricas:

| Modo | Latência | Carbono | Custo | Descrição |
|------|----------|---------|-------|-----------|
| **balanced** | 50% | 30% | 20% | Modo equilibrado - balanceia todas as métricas |
| **sustainable** | 40% | 45% | 15% | Prioriza sustentabilidade e energia limpa |
| **emergency_latency** | 70% | 15% | 15% | Prioriza performance e baixa latência |
| **emergency_cost** | 40% | 10% | 50% | Prioriza economia de custos |

## 📦 Dependências

Python 3.7+ com as seguintes bibliotecas:

```bash
numpy>=1.20.0
pandas>=1.3.0
scipy>=1.7.0
```

## 🚀 Como Usar

### 1. Instalação das Dependências

```bash
pip install -r requirements.txt
```

### 2. Gerar Dados de Simulação

```bash
python simulator/data_generator.py
```

Este comando gera:
- 20 regiões (datacenters) com características variadas
- 50 workloads com diferentes requisitos
- Salva em `results/generated_data.json`

### 3. Executar Simulações

```bash
python simulator/orchestrator.py
```

Este comando:
- Carrega os dados gerados
- Executa simulações para todos os modos operacionais
- Para cada workload, encontra a melhor região
- Salva resultados em `results/raw_results.csv`

### 4. Analisar Resultados

```bash
python analysis/analysis.py
```

Ou especifique um arquivo CSV:

```bash
python analysis/analysis.py results/raw_results.csv
```

Este comando gera:
- Relatório detalhado no console
- Arquivos CSV com análises:
  - `analysis_summary.csv` - Resumo geral
  - `analysis_by_mode.csv` - Estatísticas por modo
  - `mode_comparisons.csv` - Comparações entre modos
  - `workload_distribution.csv` - Distribuição por prioridade
