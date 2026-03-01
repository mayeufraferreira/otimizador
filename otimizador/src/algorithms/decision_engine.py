import numpy as np
from typing import List, Tuple, Optional, Dict
from src.models.region import Region
from src.models.workload import Workload
from src.algorithms.constraints import check_hard_constraints
from src.algorithms.scorer import calculate_final_score

# Definição dos modos operacionais e seus pesos para as métricas
# Cada modo prioriza diferentes aspectos do sistema
OPERATION_MODES = {
    'balanced': {  # Modo equilibrado - balanceia todas as métricas
        'latency': 0.50,  # Prioriza latência moderadamente
        'carbon': 0.30,   # Considera sustentabilidade
        'cost': 0.20      # Considera custo
    },
    'sustainable': {  # Modo sustentável - prioriza energia limpa
        'latency': 0.40,
        'carbon': 0.45,   # Máxima prioridade para sustentabilidade
        'cost': 0.15
    },
    'emergency_latency': {  # Modo emergência - prioriza performance
        'latency': 0.70,  # Máxima prioridade para baixa latência
        'carbon': 0.15,
        'cost': 0.15
    },
    'emergency_cost': {  # Modo economia - prioriza custo
        'latency': 0.40,
        'carbon': 0.10,
        'cost': 0.50      # Máxima prioridade para economia
    }
}

def decide_best_region(workload: Workload, regions: List[Region], mode: str = 'balanced') -> Tuple[Optional[Region], List[Dict]]:
    # Função principal: decide a melhor região para executar um workload
    # Retorna a melhor região e uma lista com todas as avaliações
    
    # Valida se o modo operacional informado existe
    if mode not in OPERATION_MODES:
        raise ValueError(f"Invalid mode: {mode}. Must be one of {list(OPERATION_MODES.keys())}")
    
    # Obtém os pesos das métricas baseado no modo operacional
    weights = OPERATION_MODES[mode]

    # Custo padrão no caso de faltar dados
    DEFAULT_COST_PER_KWH = 0.12
    
    # Se a lista de regiões está vazia usa o valor de custo padrão
    if not regions:
        avg_cost = DEFAULT_COST_PER_KWH
    else:
        costs = [region.cost_per_kwh for region in regions] # Extrai apenas os custos de cada região
        avg_cost = np.mean(costs) # Calcula a média real do mercado

    # Lista que armazena as avaliações de todas as regiões (log detalhado)
    evaluations = []

    # Avalia cada região individualmente
    for region in regions:
        # Verifica se a região atende aos hard constraints (CPU, latência, status)
        passed, violations = check_hard_constraints(region, workload)
        
        evaluation = {
            'region_id': region.id,
            'region_name': region.name,
            'passed_constraints': passed,
            'violations': violations,
            'scores': None
        }

        # Se a região não passou na verificação recebe nota 0 em tudo
        if not passed:
            evaluation['scores'] = {
                'latency': 0.0,
                'carbon': 0.0,
                'cost': 0.0,
                'final': 0.0
            }
        else:
            # Se a região passou, calcula todos os scores e os adiciona no log
            scores = calculate_final_score(region, workload, avg_cost, weights)
            evaluation['scores'] = scores

        evaluations.append(evaluation)

    # Cria uma nova lista com as regiões que passaram na verificação
    valid_evaluations = [e for e in evaluations if e['passed_constraints']]

    # Se não houver regiões válidas (a lista estiver vazia) retorna None
    if not valid_evaluations:
        return None, evaluations
    
    # Ordena as regiões em ordem decrescente utilizando o score final como base
    valid_evaluations.sort(key=lambda e: e['scores']['final'], reverse=True)
    
    # Seleciona o maior valor (melhor região) que é a primeira já que a lista está ordenada de forma decrescente
    best_region_id = valid_evaluations[0]['region_id']

    # Busca a região na lista de regiões passadas pelo id para retornar a região completa
    best_region = None
    for region in regions:
        if region.id == best_region_id:
            best_region = region
            break
    
    return best_region, evaluations
