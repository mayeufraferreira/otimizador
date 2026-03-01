def calculate_latency_score(region_latency_ms: float, threshold_ms: float = 2000.0) -> float:
    # Calcula o score de latência (0.0 = pior, 1.0 = melhor)
    # Latência menor é melhor → score mais alto
    
    if region_latency_ms >= threshold_ms:
        return 0.0
    
    # Score inversamente proporcional à latência
    score = 1.0 - (region_latency_ms / threshold_ms)
    return max(0.0, min(1.0, score))

def calculate_carbon_score(renewable_pct: float, carbon_intensity: float) -> float:
    # Calcula o score de sustentabilidade (0.0 = pior, 1.0 = melhor)
    # Recebe a porcentagem de energia renovável e a intensidade do carbono em g/kWh
    
    # Transforma a porcentagem em um número decimal para caber na escala (0-1)
    renewable_score = renewable_pct / 100.0

    # Score inversamente proporcional à intensidade de carbono
    # Normalizado considerando 1000 g/kWh como referência máxima
    carbon_score = max(0.0, 1.0 - (carbon_intensity / 1000.0))

    # Média ponderada com maior peso para energia renovável (70% vs 30%)
    final_score = 0.7 * renewable_score + 0.3 * carbon_score
    return max(0.0, min(1.0, final_score))

def calculate_cost_score(region_cost: float, avg_cost: float) -> float:
    # Calcula o score do custo (0.0 = pior/mais caro, 1.0 = melhor/mais barato)
    # Recebe o custo da região e a média do custo de todas as regiões
    # Permite comparar o custo relativo no momento atual
    
    if avg_cost == 0:
        return 1.0
    
    # Calcula custo relativo comparado à média
    relative_cost = region_cost / avg_cost
    
    # Score inversamente proporcional ao custo relativo
    # Custo abaixo da média = score alto, custo acima da média = score baixo
    score = 1.0 - (relative_cost - 0.5) / 1.0

    return max(0.0, min(1.0, score))

def calculate_final_score(region, workload, avg_cost: float, weights: dict) -> dict:
    # Função que calcula o score final combinando as 3 métricas principais
    # Retorna scores individuais e o score final ponderado
    
    # Score de latência (baseado no threshold do workload)
    lat_score = calculate_latency_score(region.avg_latency_ms, workload.latency_threshold_ms)

    # Score de sustentabilidade (energia renovável + intensidade de carbono)
    carbon_score = calculate_carbon_score(region.renewable_pct, region.carbon_intensity)

    # Score de custo (comparado à média do mercado)
    cost_score = calculate_cost_score(region.cost_per_kwh, avg_cost)

    # Soma final ponderada
    final = (
        weights['latency'] * lat_score +
        weights['carbon'] * carbon_score +
        weights['cost'] * cost_score
    )

    return {
        'latency': lat_score,
        'carbon': carbon_score,
        'cost': cost_score,
        'final': final
    }
