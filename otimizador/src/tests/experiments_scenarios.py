# 100 Cenários Experimentais para Artigo Científico
# Cobertura completa: sensibilidade, modos, escala, stress, limites extremos

def generate_scientific_scenarios():    
    scenarios = []
    
    # Baseline (1 cenário)
    scenarios.append({
        'scenario_id': 'baseline',
        'category': 'baseline',
        'description': 'Baseline - Valores fixos sem variação',
        'variance': 0.0,
        'mode': 'balanced',
        'n_regions': 5,
        'n_workloads': 10,
        'rounds': 30  # Aumentado para robustez estatística
    })
    
    # CATEGORIA 2: Análise de Sensibilidade - Variância (20 cenários)
    # Variância fina: -10% a +10%
    for v in [-0.10, -0.075, -0.05, -0.025, 0.025, 0.05, 0.075, 0.10]:
        scenarios.append({
            'scenario_id': f'sens_variance_{int(v*100):+03d}',
            'category': 'sensitivity_fine',
            'description': f'Sensibilidade fina: variância {v*100:+.1f}%',
            'variance': v,
            'mode': 'balanced',
            'n_regions': 5,
            'n_workloads': 10,
            'rounds': 30
        })
    
    # Variância moderada: -50% a +50% (passos de 12.5%)
    for v in [-0.50, -0.375, -0.25, -0.125, 0.125, 0.25, 0.375, 0.50]:
        scenarios.append({
            'scenario_id': f'sens_variance_{int(v*100):+03d}',
            'category': 'sensitivity_moderate',
            'description': f'Sensibilidade moderada: variância {v*100:+.1f}%',
            'variance': v,
            'mode': 'balanced',
            'n_regions': 5,
            'n_workloads': 10,
            'rounds': 30
        })
    
    # Variância extrema: -75%, -100%, +75%, +100%
    for v in [-1.0, -0.75, 0.75, 1.0]:
        scenarios.append({
            'scenario_id': f'sens_variance_extreme_{int(v*100):+03d}',
            'category': 'sensitivity_extreme',
            'description': f'Sensibilidade EXTREMA: variância {v*100:+.0f}%',
            'variance': v,
            'mode': 'balanced',
            'n_regions': 5,
            'n_workloads': 10,
            'rounds': 30
        })
    
    # Comparação de modos (16 cenários)
    modes = ['balanced', 'sustainable', 'emergency_latency', 'emergency_cost']
    variances_mode = [0.0, 0.25, 0.50, 0.75]  # 4 variâncias × 4 modos = 16
    
    for mode in modes:
        for v in variances_mode:
            v_label = f'var{int(v*100):02d}' if v > 0 else 'baseline'
            scenarios.append({
                'scenario_id': f'mode_{mode}_{v_label}',
                'category': 'mode_comparison',
                'description': f'Modo {mode} com variância {v*100:.0f}%',
                'variance': v,
                'mode': mode,
                'n_regions': 5,
                'n_workloads': 10,
                'rounds': 30
            })
    
    # Análise de Escala - Regiões (10 cenários)
    for n_reg in [3, 5, 7, 10, 15, 20, 25, 30, 40, 50]:
        scenarios.append({
            'scenario_id': f'scale_regions_{n_reg:02d}',
            'category': 'scale_regions',
            'description': f'Escala: {n_reg} regiões',
            'variance': 0.0,
            'mode': 'balanced',
            'n_regions': n_reg,
            'n_workloads': 10,
            'rounds': 20
        })
    
    # Análise de Escala - Workloads (10 cenários)
    for n_wl in [5, 10, 20, 30, 50, 75, 100, 150, 200, 250]:
        scenarios.append({
            'scenario_id': f'scale_workloads_{n_wl:03d}',
            'category': 'scale_workloads',
            'description': f'Escala: {n_wl} workloads',
            'variance': 0.0,
            'mode': 'balanced',
            'n_regions': 5,
            'n_workloads': n_wl,
            'rounds': 20
        })
    
    # Testes de Estresse (12 cenários)
    # Stress: alta variância + muitos workloads
    stress_configs = [
        (0.5, 50, 'sustainable'),
        (0.75, 50, 'sustainable'),
        (1.0, 50, 'sustainable'),
        (0.5, 100, 'balanced'),
        (0.75, 100, 'balanced'),
        (1.0, 100, 'balanced'),
    ]
    
    for i, (v, n_wl, mode) in enumerate(stress_configs, 1):
        scenarios.append({
            'scenario_id': f'stress_{i:02d}_v{int(v*100)}_wl{n_wl}',
            'category': 'stress',
            'description': f'Stress: var={v*100:.0f}%, {n_wl} workloads, {mode}',
            'variance': v,
            'mode': mode,
            'n_regions': 5,
            'n_workloads': n_wl,
            'rounds': 20
        })
    
    # Stress: muitas regiões + alta variância
    for i, (v, n_reg) in enumerate([(0.5, 30), (0.75, 30), (1.0, 30), 
                                      (0.5, 50), (0.75, 50), (1.0, 50)], 7):
        scenarios.append({
            'scenario_id': f'stress_{i:02d}_v{int(v*100)}_reg{n_reg}',
            'category': 'stress',
            'description': f'Stress: var={v*100:.0f}%, {n_reg} regiões',
            'variance': v,
            'mode': 'balanced',
            'n_regions': n_reg,
            'n_workloads': 20,
            'rounds': 20
        })
    
    # Limites Extremos (10 cenários)
    edge_cases = [
        # Mínimos
        {'n_regions': 2, 'n_workloads': 1, 'variance': 0.0, 'desc': 'Mínimo absoluto'},
        {'n_regions': 2, 'n_workloads': 5, 'variance': 0.5, 'desc': '2 regiões, var 50%'},
        
        # Máximos
        {'n_regions': 100, 'n_workloads': 10, 'variance': 0.0, 'desc': '100 regiões'},
        {'n_regions': 10, 'n_workloads': 500, 'variance': 0.0, 'desc': '500 workloads'},
        
        # Desbalanceados
        {'n_regions': 50, 'n_workloads': 5, 'variance': 0.25, 'desc': 'Muitas regiões, poucos WL'},
        {'n_regions': 3, 'n_workloads': 100, 'variance': 0.25, 'desc': 'Poucas regiões, muitos WL'},
        
        # Extremos combinados
        {'n_regions': 100, 'n_workloads': 500, 'variance': 0.0, 'desc': 'Máximo tudo (baseline)'},
        {'n_regions': 50, 'n_workloads': 250, 'variance': 0.5, 'desc': 'Alto + var 50%'},
        {'n_regions': 30, 'n_workloads': 200, 'variance': 1.0, 'desc': 'Alto + var 100%'},
        {'n_regions': 2, 'n_workloads': 500, 'variance': 1.0, 'desc': 'Pior caso possível'},
    ]
    
    for i, ec in enumerate(edge_cases, 1):
        scenarios.append({
            'scenario_id': f'edge_{i:02d}',
            'category': 'edge_case',
            'description': f'Edge: {ec["desc"]}',
            'variance': ec['variance'],
            'mode': 'balanced',
            'n_regions': ec['n_regions'],
            'n_workloads': ec['n_workloads'],
            'rounds': 15
        })
    
    # Combinações Complexas (11 cenários)
    complex_scenarios = [
        # Emergency + alta carga
        {'var': 0.5, 'mode': 'emergency_latency', 'reg': 10, 'wl': 100, 'desc': 'Emergency lat + carga'},
        {'var': 0.5, 'mode': 'emergency_cost', 'reg': 10, 'wl': 100, 'desc': 'Emergency cost + carga'},
        
        # Sustainable + stress
        {'var': 0.75, 'mode': 'sustainable', 'reg': 20, 'wl': 150, 'desc': 'Sustainable stress'},
        {'var': 1.0, 'mode': 'sustainable', 'reg': 30, 'wl': 200, 'desc': 'Sustainable extremo'},
        
        # Balanced + escala
        {'var': 0.25, 'mode': 'balanced', 'reg': 50, 'wl': 250, 'desc': 'Balanced grande escala'},
        
        # Todos os modos + variância extrema
        {'var': 1.0, 'mode': 'balanced', 'reg': 10, 'wl': 50, 'desc': 'Balanced var 100%'},
        {'var': 1.0, 'mode': 'sustainable', 'reg': 10, 'wl': 50, 'desc': 'Sustainable var 100%'},
        {'var': 1.0, 'mode': 'emergency_latency', 'reg': 10, 'wl': 50, 'desc': 'Em.Lat var 100%'},
        {'var': 1.0, 'mode': 'emergency_cost', 'reg': 10, 'wl': 50, 'desc': 'Em.Cost var 100%'},
        
        # Cenários produção-like
        {'var': 0.15, 'mode': 'balanced', 'reg': 15, 'wl': 75, 'desc': 'Produção típica'},
        {'var': 0.30, 'mode': 'sustainable', 'reg': 20, 'wl': 100, 'desc': 'Produção sustentável'},
    ]
    
    for i, cs in enumerate(complex_scenarios, 1):
        scenarios.append({
            'scenario_id': f'complex_{i:02d}',
            'category': 'complex',
            'description': f'Complexo: {cs["desc"]}',
            'variance': cs['var'],
            'mode': cs['mode'],
            'n_regions': cs['reg'],
            'n_workloads': cs['wl'],
            'rounds': 20
        })
    
    # Adicionais (10 cenários)
    # Produção-like com diferentes características
    additional_configs = [
        {'var': 0.10, 'mode': 'balanced', 'reg': 8, 'wl': 40, 'desc': 'Produção pequena'},
        {'var': 0.20, 'mode': 'balanced', 'reg': 12, 'wl': 60, 'desc': 'Produção média'},
        {'var': 0.15, 'mode': 'sustainable', 'reg': 10, 'wl': 50, 'desc': 'Eco pequena'},
        {'var': 0.25, 'mode': 'sustainable', 'reg': 18, 'wl': 90, 'desc': 'Eco média'},
        {'var': 0.30, 'mode': 'sustainable', 'reg': 25, 'wl': 120, 'desc': 'Eco grande'},
        {'var': 0.05, 'mode': 'emergency_latency', 'reg': 8, 'wl': 30, 'desc': 'Baixa latência crítico'},
        {'var': 0.10, 'mode': 'emergency_cost', 'reg': 15, 'wl': 80, 'desc': 'Custo crítico'},
        {'var': 0.40, 'mode': 'balanced', 'reg': 20, 'wl': 100, 'desc': 'Alta variabilidade'},
        {'var': 0.60, 'mode': 'sustainable', 'reg': 25, 'wl': 150, 'desc': 'Sustentável extremo'},
        {'var': 0.50, 'mode': 'balanced', 'reg': 35, 'wl': 175, 'desc': 'Grande escala variável'},
    ]
    
    for i, ac in enumerate(additional_configs, 1):
        scenarios.append({
            'scenario_id': f'additional_{i:02d}',
            'category': 'additional_realistic',
            'description': f'Adicional: {ac["desc"]}',
            'variance': ac['var'],
            'mode': ac['mode'],
            'n_regions': ac['reg'],
            'n_workloads': ac['wl'],
            'rounds': 20
        })
    
    # Verificar se existem 100 cenários
    assert len(scenarios) == 100, f"Esperado 100 cenários, obteve {len(scenarios)}"
    
    # Verificar IDs únicos
    ids = [s['scenario_id'] for s in scenarios]
    assert len(ids) == len(set(ids)), "IDs duplicados encontrados!"
    
    return scenarios

SCENARIOS = generate_scientific_scenarios()
