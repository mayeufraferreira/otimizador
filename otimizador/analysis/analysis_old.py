import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Tuple, Optional
import os
import sys

# Adiciona diretório raiz ao path para importações relativas
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


def validate_latency_threshold(df_results: pd.DataFrame, threshold_ms: float = 2000.0) -> Dict:
    """
    Valida que todas as alocações respeitem o limite máximo de latência
    
    Args:
        df_results: DataFrame com os resultados das simulações
        threshold_ms: Limite máximo de latência em milissegundos
    
    Returns:
        Dicionário com estatísticas de validação de latência
    """
    # Filtra apenas as alocações bem-sucedidas (que encontraram uma região)
    successful = df_results[df_results['best_region_id'].notna()]
    
    # Identifica violações do limite de latência
    violations = successful[successful['region_latency_ms'] > threshold_ms]
    
    total = len(successful)
    violations_count = len(violations)
    success_count = total - violations_count

    # Calcula a taxa de validação em percentual
    validation_rate = (success_count / total) * 100 if total > 0 else 0
    
    # Estatísticas de latência das alocações bem-sucedidas
    latencies = successful['region_latency_ms']
    has_data = len(successful) > 0

    return {
        'threshold_ms': threshold_ms,
        'total_allocations': len(df_results),
        'successful_allocations': total,
        'latency_violations': violations_count,
        'validation_rate_%': round(validation_rate, 2),
        'max_latency_ms': round(latencies.max(), 2) if has_data else 0,
        'mean_latency_ms': round(latencies.mean(), 2) if has_data else 0,
        'std_latency_ms': round(latencies.std(), 2) if has_data else 0,
        'passed': violations_count == 0
    }


def calculate_confidence_interval(data: np.ndarray, confidence: float = 0.95) -> Tuple[float, float, float]:
    """
    Calcula o intervalo de confiança usando distribuição t-Student
    
    Args:
        data: Array de dados numéricos
        confidence: Nível de confiança (default: 0.95 para 95%)
    
    Returns:
        Tupla (média, limite_inferior, limite_superior)
    """
    n = len(data)
    if n < 2:
        mean_val = np.mean(data) if n > 0 else 0
        return mean_val, mean_val, mean_val
    
    mean = np.mean(data)
    std_err = stats.sem(data)  # Erro padrão da média
    margin = std_err * stats.t.ppf((1 + confidence) / 2, n - 1)
    
    return mean, mean - margin, mean + margin


def calculate_allocation_metrics(df_results: pd.DataFrame) -> Dict:
    """
    Calcula métricas detalhadas de alocação com intervalo de confiança de 95%
    
    Args:
        df_results: DataFrame com os resultados das simulações
    
    Returns:
        Dicionário com métricas de sucesso de alocação
    """
    total = len(df_results)
    successful = df_results[df_results['best_region_id'].notna()]
    n_success = len(successful)
    
    # Taxa de sucesso
    success_rate = (n_success / total * 100) if total > 0 else 0
    
    # Intervalo de confiança 95% para proporção binomial
    p = success_rate / 100
    n = total
    std_err = np.sqrt(p * (1 - p) / n) if n > 0 else 0
    z = 1.96  # Valor crítico para 95% de confiança
    ci_lower = max(0, (p - z * std_err) * 100)
    ci_upper = min(100, (p + z * std_err) * 100)
    
    return {
        'total_simulations': total,
        'successful_allocations': n_success,
        'failed_allocations': total - n_success,
        'success_rate_%': round(success_rate, 2),
        'ci_95_lower_%': round(ci_lower, 2),
        'ci_95_upper_%': round(ci_upper, 2),
        'ci_95_width_%': round(ci_upper - ci_lower, 2)
    }


def calculate_performance_metrics(df_results: pd.DataFrame, confidence: float = 0.95) -> Dict:
    """
    Calcula métricas de desempenho com intervalos de confiança
    
    Args:
        df_results: DataFrame com os resultados das simulações
        confidence: Nível de confiança (default: 0.95)
    
    Returns:
        Dicionário com métricas de desempenho detalhadas
    """
    successful = df_results[df_results['best_region_id'].notna()]
    
    if len(successful) == 0:
        return {'error': 'Nenhuma alocação bem-sucedida encontrada'}
    
    metrics = {}
    
    # Métricas de Latência
    lat_mean, lat_ci_lower, lat_ci_upper = calculate_confidence_interval(
        successful['region_latency_ms'].values, confidence
    )
    metrics['latency_ms'] = {
        'mean': round(lat_mean, 2),
        'std': round(successful['region_latency_ms'].std(), 2),
        'min': round(successful['region_latency_ms'].min(), 2),
        'max': round(successful['region_latency_ms'].max(), 2),
        'ci_95_lower': round(lat_ci_lower, 2),
        'ci_95_upper': round(lat_ci_upper, 2)
    }
    
    # Energia Renovável
    ren_mean, ren_ci_lower, ren_ci_upper = calculate_confidence_interval(
        successful['region_renewable_pct'].values, confidence
    )
    metrics['renewable_%'] = {
        'mean': round(ren_mean, 2),
        'std': round(successful['region_renewable_pct'].std(), 2),
        'min': round(successful['region_renewable_pct'].min(), 2),
        'max': round(successful['region_renewable_pct'].max(), 2),
        'ci_95_lower': round(ren_ci_lower, 2),
        'ci_95_upper': round(ren_ci_upper, 2)
    }
    
    # Intensidade de Carbono
    carb_mean, carb_ci_lower, carb_ci_upper = calculate_confidence_interval(
        successful['region_carbon_intensity'].values, confidence
    )
    metrics['carbon_gCO2/kWh'] = {
        'mean': round(carb_mean, 2),
        'std': round(successful['region_carbon_intensity'].std(), 2),
        'min': round(successful['region_carbon_intensity'].min(), 2),
        'max': round(successful['region_carbon_intensity'].max(), 2),
        'ci_95_lower': round(carb_ci_lower, 2),
        'ci_95_upper': round(carb_ci_upper, 2)
    }
    
    # Custo de Energia
    cost_mean, cost_ci_lower, cost_ci_upper = calculate_confidence_interval(
        successful['region_cost_per_kwh'].values, confidence
    )
    metrics['cost_$/kWh'] = {
        'mean': round(cost_mean, 4),
        'std': round(successful['region_cost_per_kwh'].std(), 4),
        'min': round(successful['region_cost_per_kwh'].min(), 4),
        'max': round(successful['region_cost_per_kwh'].max(), 4),
        'ci_95_lower': round(cost_ci_lower, 4),
        'ci_95_upper': round(cost_ci_upper, 4)
    }
    
    return metrics


# Testes Estatísticos
def perform_statistical_tests(df_results: pd.DataFrame) -> Dict:
    baseline = df_results[df_results['scenario_id'] == 'baseline']
    sustainable = df_results[
        df_results['scenario_id'].str.contains('sustainable', case=False, na=False)
    ]
    
    if len(baseline) < 2 or len(sustainable) < 2:
        return {'error': 'Dados insuficientes para testes estatísticos'}
    
    baseline_success = baseline[baseline['success'] == True]
    sustainable_success = sustainable[sustainable['success'] == True]
    
    if len(baseline_success) < 2 or len(sustainable_success) < 2:
        return {'error': 'Alocações bem-sucedidas insuficientes'}
    
    tests = {}
    
    # Teste t para Renovável
    baseline_ren = baseline_success['renewable_pct'].values
    sustainable_ren = sustainable_success['renewable_pct'].values
    
    t_stat_ren, p_value_ren = stats.ttest_ind(sustainable_ren, baseline_ren)
    cohens_d_ren = (sustainable_ren.mean() - baseline_ren.mean()) / np.sqrt(
        (baseline_ren.std()**2 + sustainable_ren.std()**2) / 2
    )
    
    tests['renewable'] = {
        't_statistic': round(t_stat_ren, 4),
        'p_value': round(p_value_ren, 6),
        'significant': p_value_ren < 0.05,
        'cohens_d': round(cohens_d_ren, 4),
        'effect_size': 'large' if abs(cohens_d_ren) >= 0.8 else ('medium' if abs(cohens_d_ren) >= 0.5 else 'small')
    }
    
    # Teste t para Custo
    baseline_cost = baseline_success['cost_kwh'].values
    sustainable_cost = sustainable_success['cost_kwh'].values
    
    t_stat_cost, p_value_cost = stats.ttest_ind(sustainable_cost, baseline_cost)
    cohens_d_cost = (baseline_cost.mean() - sustainable_cost.mean()) / np.sqrt(
        (baseline_cost.std()**2 + sustainable_cost.std()**2) / 2
    )
    
    tests['cost'] = {
        't_statistic': round(t_stat_cost, 4),
        'p_value': round(p_value_cost, 6),
        'significant': p_value_cost < 0.05,
        'cohens_d': round(cohens_d_cost, 4),
        'effect_size': 'large' if abs(cohens_d_cost) >= 0.8 else ('medium' if abs(cohens_d_cost) >= 0.5 else 'small')
    }
    
    # Teste t para Carbono
    baseline_carb = baseline_success['carbon_intensity'].values
    sustainable_carb = sustainable_success['carbon_intensity'].values
    
    t_stat_carb, p_value_carb = stats.ttest_ind(sustainable_carb, baseline_carb)
    cohens_d_carb = (baseline_carb.mean() - sustainable_carb.mean()) / np.sqrt(
        (baseline_carb.std()**2 + sustainable_carb.std()**2) / 2
    )
    
    tests['carbon'] = {
        't_statistic': round(t_stat_carb, 4),
        'p_value': round(p_value_carb, 6),
        'significant': p_value_carb < 0.05,
        'cohens_d': round(cohens_d_carb, 4),
        'effect_size': 'large' if abs(cohens_d_carb) >= 0.8 else ('medium' if abs(cohens_d_carb) >= 0.5 else 'small')
    }
    
    return tests


# KPIS do Sistema
def calculate_kpis(df_results: pd.DataFrame) -> Dict:
    baseline = df_results[df_results['scenario_id'] == 'baseline']
    sustainable = df_results[
        df_results['scenario_id'].str.contains('sustainable', case=False, na=False)
    ]
    
    if len(baseline) == 0 or len(sustainable) == 0:
        return {'error': 'Cenários baseline ou sustainable não encontrados'}
    
    baseline_success = baseline[baseline['success'] == True]
    sustainable_success = sustainable[sustainable['success'] == True]
    
    # KPI 1: Redução de CO₂ (via % renovável)
    baseline_renewable = baseline_success['renewable_pct'].mean()
    sustainable_renewable = sustainable_success['renewable_pct'].mean()
    carbon_reduction = ((sustainable_renewable - baseline_renewable) / baseline_renewable) * 100 if baseline_renewable > 0 else 0
    
    # KPI 2: Economia de custo
    baseline_cost = baseline_success['cost_kwh'].mean()
    sustainable_cost = sustainable_success['cost_kwh'].mean()
    cost_reduction = ((baseline_cost - sustainable_cost) / baseline_cost) * 100 if baseline_cost > 0 else 0
    
    # KPI 3: Latência
    max_latency = df_results['final_latency_ms'].max()
    
    # KPI 4: Taxa de sucesso
    success_rate = (df_results['success'].sum() / len(df_results)) * 100
    
    # KPI 5: Uso renovável
    renewable_usage = sustainable_renewable
    
    kpis = {
        'carbon_reduction_%': round(carbon_reduction, 2),
        'cost_reduction_%': round(cost_reduction, 2),
        'max_latency_ms': round(max_latency, 2),
        'success_rate_%': round(success_rate, 2),
        'renewable_usage_%': round(renewable_usage, 2),
        'targets': {
            'carbon_reduction_target': 30,
            'cost_reduction_target': 25,
            'max_latency_target': 2000,
            'success_rate_target': 95,
            'renewable_usage_target': 60
        },
        'targets_met': {
            'carbon_reduction': carbon_reduction >= 30,
            'cost_reduction': cost_reduction >= 25,
            'max_latency': max_latency < 2000,
            'success_rate': success_rate >= 95,
            'renewable_usage': renewable_usage >= 60
        }
    }
    
    kpis['all_targets_met'] = all(kpis['targets_met'].values())
    
    return kpis


# 8. Análise Completa e Geração de Relatório
def generate_complete_analysis(df_results: pd.DataFrame, output_dir: str = 'results') -> Dict:
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n" + "="*80)
    print("ANÁLISE ESTATÍSTICA COMPLETA")
    print("="*80)
    
    # 1. Validação de Constraints
    print("\n  Validando constraints de latência...")
    validation = validate_latency_threshold(df_results)
    
    # 2. Métricas de Alocação
    print("Calculando métricas de alocação...")
    allocation = calculate_allocation_metrics(df_results)
    
    # 3. Métricas de Desempenho
    print("Calculando métricas de desempenho com IC 95%...")
    performance = calculate_performance_metrics(df_results)
    
    # 5. Testes Estatísticos
    print("Realizando testes estatísticos...")
    tests = perform_statistical_tests(df_results)
    
    # 6. KPIs
    print("Calculando KPIs do sistema...")
    kpis = calculate_kpis(df_results)
    
    # Consolida resultados
    results = {
        'validation': validation,
        'allocation': allocation,
        'performance': performance,
        'statistical_tests': tests,
        'kpis': kpis,
        'metadata': {
            'total_scenarios': df_results['scenario_id'].nunique(),
            'total_simulations': len(df_results),
            'confidence_level': 0.95
        }
    }
    
    # Salva CSVs
    print("\nSalvando resultados...")
    
    # CSV 1: Validação
    pd.DataFrame([validation]).to_csv(f'{output_dir}/01_validation.csv', index=False)
    print(f"{output_dir}/01_validation.csv")
    
    # CSV 2: Alocação
    pd.DataFrame([allocation]).to_csv(f'{output_dir}/02_allocation_metrics.csv', index=False)
    print(f"{output_dir}/02_allocation_metrics.csv")
    
    # CSV 3: Desempenho
    if 'error' not in performance:
        perf_data = []
        for metric_name, values in performance.items():
            perf_data.append({
                'metric': metric_name,
                'mean': values['mean'],
                'std': values['std'],
                'min': values['min'],
                'max': values['max'],
                'ci_95_lower': values['ci_95_lower'],
                'ci_95_upper': values['ci_95_upper']
            })
        pd.DataFrame(perf_data).to_csv(f'{output_dir}/03_performance_ci95.csv', index=False)
        print(f"{output_dir}/03_performance_ci95.csv")
    
    # CSV 5: Testes Estatísticos
    if 'error' not in tests:
        tests_data = []
        for metric_name, test_results in tests.items():
            tests_data.append({
                'metric': metric_name,
                't_statistic': test_results['t_statistic'],
                'p_value': test_results['p_value'],
                'significant': '✓ Yes' if test_results['significant'] else '✗ No',
                'cohens_d': test_results['cohens_d'],
                'effect_size': test_results['effect_size']
            })
        pd.DataFrame(tests_data).to_csv(f'{output_dir}/05_statistical_tests.csv', index=False)
        print(f"{output_dir}/05_statistical_tests.csv")
    
    # CSV 6: KPIs
    if 'error' not in kpis:
        kpis_data = [
            {'KPI': 'CO₂ Reduction', 'Value': f"{kpis['carbon_reduction_%']:.2f}%", 
             'Target': f"≥{kpis['targets']['carbon_reduction_target']}%", 
             'Met': '✓' if kpis['targets_met']['carbon_reduction'] else '✗'},
            {'KPI': 'Cost Reduction', 'Value': f"{kpis['cost_reduction_%']:.2f}%", 
             'Target': f"≥{kpis['targets']['cost_reduction_target']}%", 
             'Met': '✓' if kpis['targets_met']['cost_reduction'] else '✗'},
            {'KPI': 'Max Latency', 'Value': f"{kpis['max_latency_ms']:.2f}ms", 
             'Target': f"<{kpis['targets']['max_latency_target']}ms", 
             'Met': '✓' if kpis['targets_met']['max_latency'] else '✗'},
            {'KPI': 'Success Rate', 'Value': f"{kpis['success_rate_%']:.2f}%", 
             'Target': f"≥{kpis['targets']['success_rate_target']}%", 
             'Met': '✓' if kpis['targets_met']['success_rate'] else '✗'},
            {'KPI': 'Renewable Usage', 'Value': f"{kpis['renewable_usage_%']:.2f}%", 
             'Target': f"≥{kpis['targets']['renewable_usage_target']}%", 
             'Met': '✓' if kpis['targets_met']['renewable_usage'] else '✗'}
        ]
        pd.DataFrame(kpis_data).to_csv(f'{output_dir}/06_kpis.csv', index=False)
        print(f"{output_dir}/06_kpis.csv")
    
    # Printar resumo
    print("\n" + "="*80)
    print("RESUMO DOS RESULTADOS")
    print("="*80)
    
    print(f"\n VALIDAÇÃO DE CONSTRAINTS:")
    print(f"   Threshold: {validation['threshold_ms']}ms")
    print(f"   Violações: {validation['latency_violations']}")
    print(f"   Status: {'✓ PASSOU' if validation['passed'] else '✗ FALHOU'}")
    
    print(f"\n ALOCAÇÃO:")
    print(f"   Total: {allocation['total_migrations']:,}")
    print(f"   Sucesso: {allocation['successful_allocations']:,} ({allocation['success_rate_%']:.2f}%)")
    print(f"   IC 95%: [{allocation['ci_95_lower_%']:.2f}%, {allocation['ci_95_upper_%']:.2f}%]")
    
    if 'error' not in performance:
        print(f"\n DESEMPENHO (com IC 95%):")
        for metric_name, values in performance.items():
            print(f"   {metric_name}:")
            print(f"      Média: {values['mean']} ± {values['std']}")
            print(f"      IC 95%: [{values['ci_95_lower']}, {values['ci_95_upper']}]")
    
    if 'error' not in tests:
        print(f"\n TESTES ESTATÍSTICOS (a=0.05):")
        for metric_name, test in tests.items():
            sig = "SIGNIFICATIVO" if test['significant'] else "✗ Não significativo"
            print(f"   {metric_name}: p={test['p_value']:.6f} {sig}, d={test['cohens_d']:.4f} ({test['effect_size']})")
    
    if 'error' not in kpis:
        print(f"\n KPIs vs TARGETS:")
        all_met = "TODOS OS TARGETS ATINGIDOS!" if kpis['all_targets_met'] else "⚠️ Alguns targets não atingidos"
        print(f"   {all_met}")
        for key, met in kpis['targets_met'].items():
            symbol = '✓' if met else '✗'
            print(f"   {symbol} {key}")
    
    print("\n" + "="*80)
    print("ANÁLISE COMPLETA GERADA!")
    print("="*80)
    print(f"\n Arquivos salvos em: {output_dir}/")
    print("   01_validation.csv")
    print("   02_allocation_metrics.csv")
    print("   03_performance_ci95.csv")
    print("   04_efficacy_efficiency.csv")
    print("   05_statistical_tests.csv")
    print("   06_kpis.csv")
    print("\n" + "="*80)
    
    return results


if __name__ == "__main__":
    # Carrega dados
    if len(sys.argv) < 2:
        csv_file = 'results/raw_results.csv'
    else:
        csv_file = sys.argv[1]
    
    # Cria CSV mock se não existir
    if not os.path.exists(csv_file):
        print(f" Arquivo não encontrado: {csv_file}")
        print(" Criando arquivo de exemplo (mock data)...")
        
        # Garante que o diretório exista
        os.makedirs(os.path.dirname(csv_file) or '.', exist_ok=True)
        
        # Cria dados fictícios cobrindo baseline e sustainable para os testes
        mock_data = {
            'scenario_id': ['baseline', 'baseline', 'baseline', 'sustainable', 'sustainable', 'sustainable'],
            'success': [True, True, False, True, True, True],
            'final_latency_ms': [1500, 1600, 2500, 1400, 1450, 1300],
            'renewable_pct': [40, 45, 30, 80, 85, 90],
            'carbon_intensity': [300, 290, 400, 100, 90, 80],
            'cost_kwh': [0.15, 0.14, 0.20, 0.10, 0.11, 0.09]
        }
        
        # Salva o arquivo CSV
        pd.DataFrame(mock_data).to_csv(csv_file, index=False)
        print(f" Arquivo de exemplo criado com sucesso em: {csv_file}\n")
    
    print(f"\n Carregando dados de: {csv_file}")
    df = pd.read_csv(csv_file)
    print(f"{len(df):,} registros carregados")
    
    # Gera análise completa
    results = generate_complete_analysis(df, output_dir='results')
