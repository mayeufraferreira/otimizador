import numpy as np
from typing import List
import sys
import os

# Adiciona o diretório raiz ao path para importações relativas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.region import Region
from src.models.workload import Workload


def generate_regions(n: int = 5, variance: float = 0.0, seed: int = None) -> List[Region]:
    # Cria n regiões fictícias (o padrão é 5)
    # variance: variação nos valores base (0.0 = sem variação, 1.0 = alta variação)
    # seed: semente para reproduzibilidade dos resultados
    if seed is not None:
        np.random.seed(seed)

    # Baseline
    BASE_RENEWABLE_PCT = 50
    BASE_CARBON_INTENSITY = 400
    BASE_COST = 0.12
    BASE_CPU = 100
    BASE_LATENCY = 200

    REGION_NAMES = ['US-East', 'EU-West', 'Asia-SE', 'US-West', 'EU-North']

    regions = []
    for i in range(n):
        # Calcula valores utilizando a variação e aplicando limites
        renewable_pct = max(0, min(100,
            BASE_RENEWABLE_PCT * (1 + variance + np.random.uniform(-0.1, 0.1))
        ))

        carbon_intensity = max(0, 
            BASE_CARBON_INTENSITY * (1 + variance + np.random.uniform(-0.1, 0.1))
        )
        
        cost_per_kwh = max(0.05, 
            BASE_COST * (1 + variance + np.random.uniform(-0.1, 0.1))
        )
        
        cpu_available = max(10, int(
            BASE_CPU * (1 + variance + np.random.uniform(-0.1, 0.1))
        ))
        
        avg_latency_ms = max(10, 
            BASE_LATENCY * (1 + variance + np.random.uniform(-0.1, 0.1))
        )

        # Cria região
        region = Region(
            id=f"region-{i+1}",
            name=f"DC-{REGION_NAMES[i % len(REGION_NAMES)]}",
            renewable_pct=renewable_pct,
            carbon_intensity=carbon_intensity,
            cost_per_kwh=cost_per_kwh,
            cpu_available=cpu_available,
            avg_latency_ms=avg_latency_ms
        )
        regions.append(region)
    
    return regions

def generate_workloads(n: int = 10, seed: int = None) -> List[Workload]:
    # Cria n cargas de trabalho fictícias (10 por padrão)
    # seed: semente para reproduzibilidade dos resultados
    if seed is not None:
        np.random.seed(seed + 1000)  # Offset para não sobrepor com generate_regions

    workloads = []
    for i in range(n):
        workload = Workload(
            id=f"workload-{i+1}",
            cpu_required=np.random.randint(5, 30),
            latency_threshold_ms=2000.0, # Limita a latência em 2 segundos
            priority=np.random.choice(['high', 'medium', 'low'])
        )
        workloads.append(workload)

    return workloads


if __name__ == "__main__":
    import json
    from pathlib import Path
    
    # Cria o diretório de resultados se não existir
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    
    # Gera dados de simulação
    print("🔄 Gerando dados de simulação...")
    
    regions = generate_regions(n=20, variance=0.2, seed=42)
    workloads = generate_workloads(n=50, seed=42)
    
    # Prepara dados para salvar em JSON
    data = {
        "regions": [
            {
                "id": r.id,
                "name": r.name,
                "renewable_pct": r.renewable_pct,
                "carbon_intensity": r.carbon_intensity,
                "cost_per_kwh": r.cost_per_kwh,
                "cpu_available": r.cpu_available,
                "avg_latency_ms": r.avg_latency_ms,
                "status": r.status
            }
            for r in regions
        ],
        "workloads": [
            {
                "id": w.id,
                "cpu_required": w.cpu_required,
                "priority": w.priority,
                "current_region": w.current_region,
                "latency_threshold_ms": w.latency_threshold_ms
            }
            for w in workloads
        ],
        "metadata": {
            "num_regions": len(regions),
            "num_workloads": len(workloads),
            "generation_seed": 42,
            "variance": 0.2
        }
    }
    
    # Salva os dados gerados
    output_file = results_dir / "generated_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Geradas {len(regions)} regiões")
    print(f"✅ Gerados {len(workloads)} workloads")
    print(f"📁 Dados salvos em: {output_file}")
    
    # Exibe estatísticas resumidas
    print("\n📊 Estatísticas das Regiões:")
    print(f"   • Energia Renovável Média: {np.mean([r.renewable_pct for r in regions]):.1f}%")
    print(f"   • Custo Médio por kWh: ${np.mean([r.cost_per_kwh for r in regions]):.4f}")
    print(f"   • Latência Média: {np.mean([r.avg_latency_ms for r in regions]):.1f}ms")
    
    print("\n📊 Estatísticas dos Workloads:")
    print(f"   • CPU Médio Requerido: {np.mean([w.cpu_required for w in workloads]):.1f}")
    priority_counts = {p: sum(1 for w in workloads if w.priority == p) for p in ['high', 'medium', 'low']}
    print(f"   • Prioridades: High={priority_counts['high']}, Medium={priority_counts['medium']}, Low={priority_counts['low']}")
