"""
Análise dos resultados das simulações do otimizador de workloads
Compatível com os dados gerados por simulator/orchestrator.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

# Adiciona diretório raiz ao path para importações relativas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


def load_results(csv_file: str) -> pd.DataFrame:
    """
    Carrega os resultados das simulações
    
    Args:
        csv_file: Caminho para o arquivo CSV com os resultados
    
    Returns:
        DataFrame com os resultados carregados
    """
    if not Path(csv_file).exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {csv_file}")
    
    df = pd.read_csv(csv_file)
    print(f"✅ {len(df):,} registros carregados de {csv_file}")
    return df


def analyze_by_mode(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analisa os resultados agrupados por modo operacional
    
    Args:
        df: DataFrame com os resultados
    
    Returns:
        DataFrame com estatísticas por modo
    """
    # Filtra apenas alocações bem-sucedidas
    successful = df[df['best_region_id'].notna()].copy()
    
    # Agrupa por modo
    mode_stats = []
    for mode in df['mode'].unique():
        mode_data = successful[successful['mode'] == mode]
        
        if len(mode_data) == 0:
            continue
        
        stats = {
            'mode': mode,
            'total_simulations': len(df[df['mode'] == mode]),
            'successful_allocations': len(mode_data),
            'success_rate_%': (len(mode_data) / len(df[df['mode'] == mode])) * 100,
            
            # Métricas de Latência
            'latency_mean_ms': mode_data['region_latency_ms'].mean(),
            'latency_std_ms': mode_data['region_latency_ms'].std(),
            'latency_min_ms': mode_data['region_latency_ms'].min(),
            'latency_max_ms': mode_data['region_latency_ms'].max(),
            
            # Métricas de Energia Renovável
            'renewable_mean_%': mode_data['region_renewable_pct'].mean(),
            'renewable_std_%': mode_data['region_renewable_pct'].std(),
            'renewable_min_%': mode_data['region_renewable_pct'].min(),
            'renewable_max_%': mode_data['region_renewable_pct'].max(),
            
            # Métricas de Carbono
            'carbon_mean_gCO2': mode_data['region_carbon_intensity'].mean(),
            'carbon_std_gCO2': mode_data['region_carbon_intensity'].std(),
            'carbon_min_gCO2': mode_data['region_carbon_intensity'].min(),
            'carbon_max_gCO2': mode_data['region_carbon_intensity'].max(),
            
            # Métricas de Custo
            'cost_mean_$kwh': mode_data['region_cost_per_kwh'].mean(),
            'cost_std_$kwh': mode_data['region_cost_per_kwh'].std(),
            'cost_min_$kwh': mode_data['region_cost_per_kwh'].min(),
            'cost_max_$kwh': mode_data['region_cost_per_kwh'].max(),
            
            # Métricas de Score
            'score_final_mean': mode_data['score_final'].mean(),
            'score_final_std': mode_data['score_final'].std(),
            'score_final_min': mode_data['score_final'].min(),
            'score_final_max': mode_data['score_final'].max(),
        }
        
        mode_stats.append(stats)
    
    return pd.DataFrame(mode_stats)


def compare_modes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compara diferentes modos operacionais
    
    Args:
        df: DataFrame com os resultados
    
    Returns:
        DataFrame com comparação entre modos
    """
    successful = df[df['best_region_id'].notna()].copy()
    
    if 'balanced' not in successful['mode'].values:
        print("⚠️  Modo 'balanced' não encontrado para comparação")
        return pd.DataFrame()
    
    # Usa 'balanced' como baseline
    baseline = successful[successful['mode'] == 'balanced']
    
    comparisons = []
    for mode in successful['mode'].unique():
        if mode == 'balanced':
            continue
        
        mode_data = successful[successful['mode'] == mode]
        
        if len(mode_data) == 0:
            continue
        
        # Calcula diferenças percentuais em relação ao baseline
        comp = {
            'mode': mode,
            'vs_baseline': 'balanced',
            
            'latency_diff_%': ((mode_data['region_latency_ms'].mean() - 
                               baseline['region_latency_ms'].mean()) / 
                              baseline['region_latency_ms'].mean() * 100),
            
            'renewable_diff_%': ((mode_data['region_renewable_pct'].mean() - 
                                 baseline['region_renewable_pct'].mean()) / 
                                baseline['region_renewable_pct'].mean() * 100),
            
            'carbon_diff_%': ((mode_data['region_carbon_intensity'].mean() - 
                              baseline['region_carbon_intensity'].mean()) / 
                             baseline['region_carbon_intensity'].mean() * 100),
            
            'cost_diff_%': ((mode_data['region_cost_per_kwh'].mean() - 
                            baseline['region_cost_per_kwh'].mean()) / 
                           baseline['region_cost_per_kwh'].mean() * 100),
            
            'score_diff_%': ((mode_data['score_final'].mean() - 
                             baseline['score_final'].mean()) / 
                            baseline['score_final'].mean() * 100),
        }
        
        comparisons.append(comp)
    
    return pd.DataFrame(comparisons)


def analyze_workload_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analisa a distribuição de workloads e sua taxa de sucesso
    
    Args:
        df: DataFrame com os resultados
    
    Returns:
        DataFrame com estatísticas por prioridade de workload
    """
    priority_stats = []
    
    for priority in df['workload_priority'].unique():
        priority_data = df[df['workload_priority'] == priority]
        successful = priority_data[priority_data['best_region_id'].notna()]
        
        stats = {
            'priority': priority,
            'total_workloads': len(priority_data),
            'successful': len(successful),
            'failed': len(priority_data) - len(successful),
            'success_rate_%': (len(successful) / len(priority_data)) * 100 if len(priority_data) > 0 else 0,
            'avg_cpu_required': priority_data['workload_cpu'].mean(),
            'avg_score': successful['score_final'].mean() if len(successful) > 0 else 0,
        }
        
        priority_stats.append(stats)
    
    return pd.DataFrame(priority_stats)


def generate_summary_report(df: pd.DataFrame) -> dict:
    """
    Gera um relatório resumido das simulações
    
    Args:
        df: DataFrame com os resultados
    
    Returns:
        Dicionário com estatísticas gerais
    """
    successful = df[df['best_region_id'].notna()]
    
    report = {
        'total_simulations': len(df),
        'successful_allocations': len(successful),
        'failed_allocations': len(df) - len(successful),
        'overall_success_rate_%': (len(successful) / len(df)) * 100 if len(df) > 0 else 0,
        
        'unique_modes': df['mode'].nunique(),
        'unique_workloads': df['workload_id'].nunique(),
        'unique_regions_selected': successful['best_region_id'].nunique() if len(successful) > 0 else 0,
        
        'avg_valid_regions_per_workload': df['num_valid_regions'].mean(),
        'avg_score_final': successful['score_final'].mean() if len(successful) > 0 else 0,
        
        # Melhor e pior casos
        'best_score': successful['score_final'].max() if len(successful) > 0 else 0,
        'worst_score': successful['score_final'].min() if len(successful) > 0 else 0,
    }
    
    return report


def print_formatted_report(summary: dict, mode_analysis: pd.DataFrame, 
                          comparisons: pd.DataFrame, workload_dist: pd.DataFrame):
    """
    Imprime um relatório formatado no console
    
    Args:
        summary: Dicionário com estatísticas gerais
        mode_analysis: DataFrame com análise por modo
        comparisons: DataFrame com comparações entre modos
        workload_dist: DataFrame com distribuição de workloads
    """
    print("\n" + "="*80)
    print("📊 RELATÓRIO DE ANÁLISE - OTIMIZADOR DE WORKLOADS")
    print("="*80)
    
    print("\n📈 RESUMO GERAL")
    print("-" * 80)
    print(f"   Total de Simulações: {summary['total_simulations']:,}")
    print(f"   Alocações Bem-sucedidas: {summary['successful_allocations']:,} "
          f"({summary['overall_success_rate_%']:.2f}%)")
    print(f"   Alocações Falhadas: {summary['failed_allocations']:,}")
    print(f"   Modos Testados: {summary['unique_modes']}")
    print(f"   Workloads Únicos: {summary['unique_workloads']}")
    print(f"   Regiões Diferentes Selecionadas: {summary['unique_regions_selected']}")
    print(f"   Média de Regiões Válidas por Workload: {summary['avg_valid_regions_per_workload']:.2f}")
    print(f"   Score Final Médio: {summary['avg_score_final']:.4f}")
    print(f"   Melhor Score: {summary['best_score']:.4f}")
    print(f"   Pior Score: {summary['worst_score']:.4f}")
    
    if not mode_analysis.empty:
        print("\n🔧 ANÁLISE POR MODO OPERACIONAL")
        print("-" * 80)
        for _, row in mode_analysis.iterrows():
            print(f"\n   Modo: {row['mode'].upper()}")
            print(f"      Taxa de Sucesso: {row['success_rate_%']:.2f}%")
            print(f"      Latência Média: {row['latency_mean_ms']:.2f}ms "
                  f"(±{row['latency_std_ms']:.2f}ms)")
            print(f"      Energia Renovável Média: {row['renewable_mean_%']:.2f}% "
                  f"(±{row['renewable_std_%']:.2f}%)")
            print(f"      Carbono Médio: {row['carbon_mean_gCO2']:.2f} gCO2/kWh "
                  f"(±{row['carbon_std_gCO2']:.2f})")
            print(f"      Custo Médio: ${row['cost_mean_$kwh']:.4f}/kWh "
                  f"(±${row['cost_std_$kwh']:.4f})")
            print(f"      Score Final Médio: {row['score_final_mean']:.4f} "
                  f"(±{row['score_final_std']:.4f})")
    
    if not comparisons.empty:
        print("\n⚖️  COMPARAÇÃO COM MODO BALANCED (baseline)")
        print("-" * 80)
        for _, row in comparisons.iterrows():
            print(f"\n   Modo: {row['mode'].upper()}")
            print(f"      Latência: {row['latency_diff_%']:+.2f}%")
            print(f"      Energia Renovável: {row['renewable_diff_%']:+.2f}%")
            print(f"      Carbono: {row['carbon_diff_%']:+.2f}%")
            print(f"      Custo: {row['cost_diff_%']:+.2f}%")
            print(f"      Score Final: {row['score_diff_%']:+.2f}%")
    
    if not workload_dist.empty:
        print("\n📦 DISTRIBUIÇÃO POR PRIORIDADE DE WORKLOAD")
        print("-" * 80)
        for _, row in workload_dist.iterrows():
            print(f"\n   Prioridade: {row['priority'].upper()}")
            print(f"      Total: {int(row['total_workloads'])} workloads")
            print(f"      Sucesso: {int(row['successful'])} ({row['success_rate_%']:.2f}%)")
            print(f"      CPU Médio Requerido: {row['avg_cpu_required']:.1f}")
            print(f"      Score Médio: {row['avg_score']:.4f}")
    
    print("\n" + "="*80)


def save_analysis_to_csv(df: pd.DataFrame, summary: dict, mode_analysis: pd.DataFrame,
                        comparisons: pd.DataFrame, workload_dist: pd.DataFrame, 
                        output_dir: str = "results"):
    """
    Salva todas as análises em arquivos CSV
    
    Args:
        df: DataFrame com os resultados originais
        summary: Dicionário com estatísticas gerais
        mode_analysis: DataFrame com análise por modo
        comparisons: DataFrame com comparações entre modos
        workload_dist: DataFrame com distribuição de workloads
        output_dir: Diretório onde salvar os arquivos
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Salva resumo geral
    pd.DataFrame([summary]).to_csv(output_path / "analysis_summary.csv", index=False)
    
    # Salva análise por modo
    if not mode_analysis.empty:
        mode_analysis.to_csv(output_path / "analysis_by_mode.csv", index=False)
    
    # Salva comparações
    if not comparisons.empty:
        comparisons.to_csv(output_path / "mode_comparisons.csv", index=False)
    
    # Salva distribuição de workloads
    if not workload_dist.empty:
        workload_dist.to_csv(output_path / "workload_distribution.csv", index=False)
    
    print(f"\n💾 Arquivos salvos em: {output_path.absolute()}/")
    print("   • analysis_summary.csv")
    print("   • analysis_by_mode.csv")
    print("   • mode_comparisons.csv")
    print("   • workload_distribution.csv")


def main(csv_file: str = "results/raw_results.csv"):
    """
    Função principal que executa toda a análise
    
    Args:
        csv_file: Caminho para o arquivo CSV com os resultados
    """
    print("\n🔍 Iniciando análise dos resultados...")
    
    try:
        # Carrega os dados
        df = load_results(csv_file)
        
        # Gera análises
        print("\n⚙️  Processando análises...")
        summary = generate_summary_report(df)
        mode_analysis = analyze_by_mode(df)
        comparisons = compare_modes(df)
        workload_dist = analyze_workload_distribution(df)
        
        # Imprime relatório
        print_formatted_report(summary, mode_analysis, comparisons, workload_dist)
        
        # Salva arquivos CSV
        save_analysis_to_csv(df, summary, mode_analysis, comparisons, 
                            workload_dist, output_dir="results")
        
        print("\n✅ Análise concluída com sucesso!")
        print("="*80 + "\n")
        
    except FileNotFoundError as e:
        print(f"\n❌ Erro: {e}")
        print("\n💡 Execute primeiro:")
        print("   1. python simulator/data_generator.py")
        print("   2. python simulator/orchestrator.py")
        print("   3. python analysis/analysis.py\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro durante a análise: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Permite passar o arquivo CSV como argumento
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        csv_file = "results/raw_results.csv"
    
    main(csv_file)
