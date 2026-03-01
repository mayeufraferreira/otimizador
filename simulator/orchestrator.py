import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List
import sys
import os

# Adiciona o diretório raiz ao path para importações relativas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.region import Region
from src.models.workload import Workload
from src.algorithms.decision_engine import decide_best_region

def load_generated_data():
    """Carrega dados gerados pelo data_generator.py"""
    data_file = Path("results/generated_data.json")
    
    if not data_file.exists():
        raise FileNotFoundError(
            f"Arquivo {data_file} não encontrado!\n"
            "Execute primeiro: python simulator/data_generator.py"
        )
    
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Reconstrói os objetos Region e Workload
    regions = [Region(**r) for r in data["regions"]]
    workloads = [Workload(**w) for w in data["workloads"]]
    
    return regions, workloads

def run_simulations(modes: List[str] = None):
    """
    Executa simulações para todos os workloads em todas as regiões
    
    Args:
        modes: Lista de modos operacionais a testar (default: ['balanced'])
    """
    if modes is None:
        modes = ['balanced']
    
    print("🔄 Carregando dados de simulação...")
    regions, workloads = load_generated_data()
    
    print(f"📊 {len(regions)} regiões carregadas")
    print(f"📊 {len(workloads)} workloads carregados")
    print(f"🎯 Testando modos: {', '.join(modes)}")
    print(f"🔢 Total de simulações: {len(workloads) * len(modes)}\n")
    
    results = []
    simulation_count = 0
    total_simulations = len(workloads) * len(modes)
    
    # Para cada modo operacional
    for mode in modes:
        print(f"\n{'='*60}")
        print(f"🔧 Executando modo: {mode.upper()}")
        print(f"{'='*60}")
        
        # Para cada workload, encontra a melhor região
        for workload in workloads:
            simulation_count += 1
            
            # Executa o motor de decisão
            best_region, evaluations = decide_best_region(workload, regions, mode=mode)
            
            # Registra o resultado
            result = {
                "simulation_id": simulation_count,
                "mode": mode,
                "workload_id": workload.id,
                "workload_cpu": workload.cpu_required,
                "workload_priority": workload.priority,
                "workload_latency_threshold": workload.latency_threshold_ms,
                "best_region_id": best_region.id if best_region else None,
                "best_region_name": best_region.name if best_region else "None",
                "num_valid_regions": sum(1 for e in evaluations if e['passed_constraints']),
                "num_total_regions": len(evaluations)
            }
            
            # Se encontrou região válida, adiciona seus detalhes e scores
            if best_region:
                best_eval = next(e for e in evaluations if e['region_id'] == best_region.id)
                result.update({
                    "region_renewable_pct": best_region.renewable_pct,
                    "region_carbon_intensity": best_region.carbon_intensity,
                    "region_cost_per_kwh": best_region.cost_per_kwh,
                    "region_cpu_available": best_region.cpu_available,
                    "region_latency_ms": best_region.avg_latency_ms,
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
            
            # Feedback de progresso
            if simulation_count % 10 == 0 or simulation_count == total_simulations:
                progress = (simulation_count / total_simulations) * 100
                print(f"   Progresso: {simulation_count}/{total_simulations} ({progress:.1f}%) - "
                      f"Workload: {workload.id} → Região: {result['best_region_name']}")
    
    # Converte para DataFrame e salva
    df = pd.DataFrame(results)
    
    # Cria diretório de resultados se não existir
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    
    # Salva resultados
    output_file = results_dir / "raw_results.csv"
    df.to_csv(output_file, index=False)
    
    print(f"\n{'='*60}")
    print(f"✅ Simulações concluídas!")
    print(f"📁 Resultados salvos em: {output_file}")
    print(f"\n📊 Resumo:")
    print(f"   • Total de simulações: {len(results)}")
    print(f"   • Regiões válidas encontradas: {df['best_region_id'].notna().sum()}")
    print(f"   • Sem região válida: {df['best_region_id'].isna().sum()}")
    
    if not df.empty and 'score_final' in df.columns:
        print(f"\n📈 Estatísticas dos Scores:")
        print(f"   • Score Final Médio: {df['score_final'].mean():.4f}")
        print(f"   • Score Final Máximo: {df['score_final'].max():.4f}")
        print(f"   • Score Final Mínimo: {df['score_final'].min():.4f}")
    
    print(f"\n💡 Execute a análise com:")
    print(f"   python analysis/analysis.py results/raw_results.csv")
    print(f"{'='*60}\n")
    
    return df

if __name__ == "__main__":
    # Executa simulações para todos os modos operacionais
    run_simulations(modes=['balanced', 'sustainable', 'emergency_latency', 'emergency_cost'])
