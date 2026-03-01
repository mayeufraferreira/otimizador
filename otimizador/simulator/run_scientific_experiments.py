"""
Executa os 100 cenários científicos com múltiplas repetições para rigor estatístico
Metodologia: Cada cenário é executado 100 vezes com seeds diferentes para reproduzibilidade
Total esperado: ~10.000+ simulações
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os
from datetime import datetime
from typing import Dict

# Adiciona o diretório raiz ao path para importações relativas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.region import Region
from src.models.workload import Workload
from src.algorithms.decision_engine import decide_best_region
from src.tests.experiments_scenarios import SCENARIOS
from simulator.data_generator import generate_regions, generate_workloads


def run_scientific_experiments(rounds_per_scenario: int = 100, save_interval: int = 1000):
    """
    Executa os 100 cenários científicos com múltiplas repetições
    
    Args:
        rounds_per_scenario: Número de repetições para cada cenário (default: 100)
        save_interval: Salva resultados intermediários a cada N simulações
    
    Returns:
        DataFrame com todos os resultados
    """
    print("\n" + "="*80)
    print("🔬 EXECUÇÃO DE EXPERIMENTOS CIENTÍFICOS - METODOLOGIA RIGOROSA")
    print("="*80)
    print(f"📊 Total de cenários científicos: {len(SCENARIOS)}")
    print(f"🔁 Repetições por cenário (rounds): {rounds_per_scenario}")
    
    # Calcula total aproximado de simulações
    total_simulations = sum(
        scenario['n_workloads'] * rounds_per_scenario 
        for scenario in SCENARIOS
    )
    print(f"🔢 Total ESTIMADO de simulações: {total_simulations:,}")
    print(f"📝 Nota: Cada cenário tem diferentes quantidades de workloads")
    print("="*80 + "\n")
    
    results = []
    simulation_count = 0
    start_time = datetime.now()
    
    # Cria diretório de resultados
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    output_file = results_dir / "raw_results.csv"
    
    # Para cada cenário científico (1 a 100)
    for scenario_idx, scenario in enumerate(SCENARIOS, 1):
        scenario_id = scenario['scenario_id']
        category = scenario['category']
        mode = scenario['mode']
        n_regions = scenario['n_regions']
        n_workloads = scenario['n_workloads']
        variance = scenario['variance']
        
        print(f"\n{'='*80}")
        print(f"📋 CENÁRIO {scenario_idx}/100: {scenario_id}")
        print(f"{'='*80}")
        print(f"   📂 Categoria: {category}")
        print(f"   📖 Descrição: {scenario['description']}")
        print(f"   ⚙️  Configuração:")
        print(f"      • Modo operacional: {mode}")
        print(f"      • Número de regiões: {n_regions}")
        print(f"      • Número de workloads: {n_workloads}")
        print(f"      • Variância: {variance*100:.1f}%")
        print(f"   🔁 Executando {rounds_per_scenario} rounds...")
        print("-" * 80)
        
        scenario_start = datetime.now()
        
        # Para cada round (repetição) do cenário
        for round_num in range(1, rounds_per_scenario + 1):
            # Gera dados com seed único para reproduzibilidade
            # Combina scenario_id e round_num para garantir seeds únicos
            seed = abs(hash(f"{scenario_id}_{round_num}")) % (2**31)
            
            # Gera regiões e workloads para este round
            regions = generate_regions(n=n_regions, variance=variance, seed=seed)
            workloads = generate_workloads(n=n_workloads, seed=seed)
            
            # Para cada workload, encontra a melhor região
            for workload_idx, workload in enumerate(workloads, 1):
                simulation_count += 1
                
                # Executa o motor de decisão
                best_region, evaluations = decide_best_region(workload, regions, mode=mode)
                
                # Registra o resultado completo
                result = {
                    # Identificadores
                    "simulation_id": simulation_count,
                    "scenario_id": scenario_id,
                    "scenario_idx": scenario_idx,
                    "scenario_category": category,
                    "round": round_num,
                    "seed": seed,
                    
                    # Configuração do cenário
                    "mode": mode,
                    "variance": variance,
                    "n_regions": n_regions,
                    "n_workloads": n_workloads,
                    
                    # Informações do workload
                    "workload_id": workload.id,
                    "workload_idx": workload_idx,
                    "workload_cpu": workload.cpu_required,
                    "workload_priority": workload.priority,
                    "workload_latency_threshold": workload.latency_threshold_ms,
                    
                    # Resultado da alocação
                    "best_region_id": best_region.id if best_region else None,
                    "best_region_name": best_region.name if best_region else "None",
                    "num_valid_regions": sum(1 for e in evaluations if e['passed_constraints']),
                    "num_total_regions": len(evaluations),
                    "allocation_success": best_region is not None
                }
                
                # Se encontrou região válida, adiciona detalhes e scores
                if best_region:
                    best_eval = next(e for e in evaluations if e['region_id'] == best_region.id)
                    result.update({
                        # Características da região escolhida
                        "region_renewable_pct": best_region.renewable_pct,
                        "region_carbon_intensity": best_region.carbon_intensity,
                        "region_cost_per_kwh": best_region.cost_per_kwh,
                        "region_cpu_available": best_region.cpu_available,
                        "region_latency_ms": best_region.avg_latency_ms,
                        
                        # Scores individuais
                        "score_latency": best_eval['scores']['latency'],
                        "score_carbon": best_eval['scores']['carbon'],
                        "score_cost": best_eval['scores']['cost'],
                        "score_final": best_eval['scores']['final']
                    })
                else:
                    # Nenhuma região válida encontrada
                    result.update({
                        "region_renewable_pct": None,
                        "region_carbon_intensity": None,
                        "region_cost_per_kwh": None,
                        "region_cpu_available": None,
                        "region_latency_ms": None,
                        "score_latency": 0.0,
                        "score_carbon": 0.0,
                        "score_cost": 0.0,
                        "score_final": 0.0
                    })
                
                results.append(result)
            
            # Feedback de progresso a cada 10 rounds
            if round_num % 10 == 0 or round_num == rounds_per_scenario:
                elapsed = (datetime.now() - start_time).total_seconds()
                rate = simulation_count / elapsed if elapsed > 0 else 0
                eta_seconds = (total_simulations - simulation_count) / rate if rate > 0 else 0
                eta_minutes = eta_seconds / 60
                
                progress_cenario = (round_num / rounds_per_scenario) * 100
                progress_total = (simulation_count / total_simulations) * 100
                
                print(f"   Round {round_num:3d}/{rounds_per_scenario} ({progress_cenario:5.1f}%) | "
                      f"Total: {simulation_count:6,}/{total_simulations:,} ({progress_total:5.2f}%) | "
                      f"{rate:5.1f} sim/s | "
                      f"ETA: {eta_minutes:6.1f}min")
            
            # Salva checkpoint intermediário
            if simulation_count % save_interval == 0:
                df_temp = pd.DataFrame(results)
                df_temp.to_csv(output_file, index=False)
                print(f"   💾 Checkpoint: {simulation_count:,} simulações salvas")
        
        # Resumo do cenário
        scenario_elapsed = (datetime.now() - scenario_start).total_seconds()
        scenario_sims = n_workloads * rounds_per_scenario
        print(f"\n   ✅ Cenário {scenario_idx} concluído em {scenario_elapsed:.1f}s")
        print(f"   📊 {scenario_sims:,} simulações deste cenário")
    
    # Salva resultados finais
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    
    elapsed_total = (datetime.now() - start_time).total_seconds()
    elapsed_hours = elapsed_total / 3600
    
    # Estatísticas finais
    successful = df[df['allocation_success'] == True]
    
    print(f"\n{'='*80}")
    print(f"✅ EXPERIMENTOS CIENTÍFICOS CONCLUÍDOS COM SUCESSO!")
    print(f"{'='*80}")
    print(f"📁 Resultados salvos em: {output_file.absolute()}")
    print(f"\n📊 RESUMO FINAL:")
    print(f"   • Total de simulações realizadas: {len(results):,}")
    print(f"   • Cenários científicos executados: {len(SCENARIOS)}")
    print(f"   • Repetições (rounds) por cenário: {rounds_per_scenario}")
    print(f"   • Tempo total de execução: {elapsed_total/60:.2f} minutos ({elapsed_hours:.2f} horas)")
    print(f"   • Velocidade média: {len(results)/elapsed_total:.1f} simulações/segundo")
    
    print(f"\n📈 TAXA DE SUCESSO:")
    print(f"   • Alocações bem-sucedidas: {len(successful):,} ({len(successful)/len(df)*100:.2f}%)")
    print(f"   • Falhas (sem região válida): {len(df) - len(successful):,} ({(len(df)-len(successful))/len(df)*100:.2f}%)")
    
    if len(successful) > 0:
        print(f"\n🎯 ESTATÍSTICAS DOS SCORES (apenas casos bem-sucedidos):")
        print(f"   • Score Final:")
        print(f"      - Média: {successful['score_final'].mean():.4f}")
        print(f"      - Desvio Padrão: {successful['score_final'].std():.4f}")
        print(f"      - Mínimo: {successful['score_final'].min():.4f}")
        print(f"      - Máximo: {successful['score_final'].max():.4f}")
        print(f"      - Mediana: {successful['score_final'].median():.4f}")
        
        print(f"\n   • Score de Latência:")
        print(f"      - Média: {successful['score_latency'].mean():.4f} ± {successful['score_latency'].std():.4f}")
        
        print(f"\n   • Score de Sustentabilidade (Carbono):")
        print(f"      - Média: {successful['score_carbon'].mean():.4f} ± {successful['score_carbon'].std():.4f}")
        
        print(f"\n   • Score de Custo:")
        print(f"      - Média: {successful['score_cost'].mean():.4f} ± {successful['score_cost'].std():.4f}")
    
    print(f"\n💡 PRÓXIMOS PASSOS:")
    print(f"   1. Análise estatística detalhada:")
    print(f"      python analysis/analysis.py results/raw_results.csv")
    print(f"\n   2. Os dados incluem:")
    print(f"      • 100 cenários científicos diferentes")
    print(f"      • {rounds_per_scenario} repetições de cada cenário")
    print(f"      • Seeds únicos para reproduzibilidade")
    print(f"      • Todas as métricas de decisão")
    
    print(f"\n{'='*80}\n")
    
    return df


def print_scenarios_summary():
    """Imprime um resumo dos 100 cenários científicos"""
    from collections import Counter
    
    print("\n" + "="*80)
    print("📚 RESUMO DOS 100 CENÁRIOS CIENTÍFICOS")
    print("="*80)
    
    # Agrupa por categoria
    categories = Counter(s['category'] for s in SCENARIOS)
    modes = Counter(s['mode'] for s in SCENARIOS)
    
    print(f"\n📊 Distribuição por Categoria:")
    for cat, count in sorted(categories.items()):
        print(f"   • {cat:30s}: {count:3d} cenários")
    
    print(f"\n🔧 Distribuição por Modo Operacional:")
    for mode, count in sorted(modes.items()):
        print(f"   • {mode:30s}: {count:3d} cenários")
    
    print(f"\n📐 Estatísticas de Configuração:")
    n_regions_list = [s['n_regions'] for s in SCENARIOS]
    n_workloads_list = [s['n_workloads'] for s in SCENARIOS]
    variances = [s['variance'] for s in SCENARIOS]
    
    print(f"   • Regiões por cenário:")
    print(f"      - Mínimo: {min(n_regions_list)}")
    print(f"      - Máximo: {max(n_regions_list)}")
    print(f"      - Média: {np.mean(n_regions_list):.1f}")
    
    print(f"   • Workloads por cenário:")
    print(f"      - Mínimo: {min(n_workloads_list)}")
    print(f"      - Máximo: {max(n_workloads_list)}")
    print(f"      - Média: {np.mean(n_workloads_list):.1f}")
    
    print(f"   • Variância:")
    print(f"      - Mínima: {min(variances)*100:.1f}%")
    print(f"      - Máxima: {max(variances)*100:.1f}%")
    print(f"      - Média: {np.mean(variances)*100:.1f}%")
    
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Executa experimentos científicos do otimizador com rigor estatístico',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Teste rápido (10 repetições por cenário)
  python simulator/run_scientific_experiments.py --rounds 10

  # Teste intermediário (30 repetições)
  python simulator/run_scientific_experiments.py --rounds 30

  # Experimento completo para publicação (100 repetições)
  python simulator/run_scientific_experiments.py --rounds 100

  # Ver resumo dos cenários sem executar
  python simulator/run_scientific_experiments.py --summary-only
        """
    )
    
    parser.add_argument('--rounds', type=int, default=100,
                       help='Número de repetições por cenário (default: 100)')
    parser.add_argument('--save-interval', type=int, default=1000,
                       help='Salva checkpoint a cada N simulações (default: 1000)')
    parser.add_argument('--summary-only', action='store_true',
                       help='Apenas mostra resumo dos cenários sem executar')
    
    args = parser.parse_args()
    
    if args.summary_only:
        print_scenarios_summary()
    else:
        print(f"\n⚙️  CONFIGURAÇÃO DA EXECUÇÃO:")
        print(f"   • Repetições (rounds) por cenário: {args.rounds}")
        print(f"   • Intervalo de checkpoint: a cada {args.save_interval} simulações")
        print(f"   • Total de cenários: {len(SCENARIOS)}")
        
        if args.rounds < 30:
            print(f"\n⚠️  AVISO: Usando apenas {args.rounds} repetições")
            print(f"   Para rigor estatístico, recomenda-se 100 repetições")
            print(f"   Use --rounds 100 para experimentos científicos")
        
        # Mostrar resumo antes de começar
        print_scenarios_summary()
        
        # Confirmar antes de executar
        try:
            input("\n⏸️  Pressione ENTER para iniciar os experimentos (Ctrl+C para cancelar)...")
        except KeyboardInterrupt:
            print("\n\n❌ Execução cancelada pelo usuário.\n")
            sys.exit(0)
        
        # Executar experimentos
        run_scientific_experiments(
            rounds_per_scenario=args.rounds,
            save_interval=args.save_interval
        )
