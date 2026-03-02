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

### 5. Executar Experimentos de Teste

```bash
python src/tests/run_experiments.py
```

Este comando:
- Executa cenários de teste predefinidos
- Valida o comportamento do motor de decisão
- Testa diferentes modos operacionais com workloads específicos

### 6. Executar Experimentos Científicos

```bash
python simulator/run_scientific_experiments.py
```

Este comando:
- Executa experimentos científicos completos
- Gera dados estatísticos detalhados
- Realiza análises comparativas entre os modos operacionais

### 7. Gerar Visualizações e Gráficos

```bash
python analysis/visualizations.py results/raw_results.csv
```

Ou especifique um diretório de saída customizado:

```bash
python analysis/visualizations.py results/raw_results.csv results/visualizations
```

Este comando gera automaticamente todos os tipos de gráficos:
- **Comparação por Modo Operacional**: Métricas comparativas entre modos com box plots e intervalos de confiança (95%)
- **Análise de Scores**: Distribuição de scores individuais (latência, carbono, custo) e score final por modo
- **Métricas Separadas**: Gráficos detalhados individuais para cada métrica (latência, renovável, carbono, custo, score)
- **Análise por Cenários**: Performance por categoria de cenário científico
- **Sensibilidade à Variância**: Impacto da variância nas métricas e scores
- **Distribuição de Regiões**: Top regiões mais selecionadas geral e por modo operacional
- **Análise por Prioridade**: Métricas agrupadas por prioridade de workload
- **Escalabilidade**: Análise de impacto do número de regiões e workloads
- **Correlações**: Mapa de calor de correlações entre métricas e scores
- **Taxa de Sucesso**: Taxa de alocação bem-sucedida por modo
- **Métricas por Região**: Análise individual de latência, custo e sustentabilidade por região (Top 20)
- **Trade-offs**: Análise de compromissos entre latência vs sustentabilidade, latência vs custo, e custo vs sustentabilidade
- **Distribuição por Cenário com IC**: Latência, custo e sustentabilidade por categoria de cenário com intervalos de confiança (95%)
- **Análise DoE/Fatorial**: Design of Experiments completo com efeitos principais, interações e diagrama de Pareto

Todos os gráficos são salvos em formato PNG de alta resolução (300 DPI).

📖 **Para descrição detalhada de cada gráfico, consulte**: [analysis/VISUALIZATIONS_GUIDE.md](analysis/VISUALIZATIONS_GUIDE.md)