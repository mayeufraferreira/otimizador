from src.tests.experiments_scenarios import SCENARIOS

# Gera os cenários
SCIENTIFIC_SCENARIOS = SCENARIOS

def print_scenario_summary():
    """Imprime resumo dos cenários por categoria."""
    from collections import Counter
    
    categories = [s['category'] for s in SCIENTIFIC_SCENARIOS]
    category_counts = Counter(categories)
    
    print("\n" + "="*70)
    print("RESUMO DOS 100 CENÁRIOS CIENTÍFICOS")
    print("="*70)
    
    total_rounds = sum(s['rounds'] for s in SCIENTIFIC_SCENARIOS)
    total_sims = sum(s['rounds'] * s['n_workloads'] for s in SCIENTIFIC_SCENARIOS)
    
    print(f"\nTotal de cenários: {len(SCIENTIFIC_SCENARIOS)}")
    print(f"Total de rounds: {total_rounds}")
    print(f"Total de simulações: {total_sims:,}")
    
    print("\n Distribuição por Categoria:")
    print("-" * 70)
    for cat, count in sorted(category_counts.items()):
        print(f"  {cat:25s}: {count:3d} cenários")
    
    print("\n Estatísticas:")
    print("-" * 70)
    regions_range = [s['n_regions'] for s in SCIENTIFIC_SCENARIOS]
    workloads_range = [s['n_workloads'] for s in SCIENTIFIC_SCENARIOS]
    variance_range = [s['variance'] for s in SCIENTIFIC_SCENARIOS]
    
    print(f"  Regiões:   {min(regions_range):3d} a {max(regions_range):3d}")
    print(f"  Workloads: {min(workloads_range):3d} a {max(workloads_range):3d}")
    print(f"  Variância: {min(variance_range)*100:6.1f}% a {max(variance_range)*100:6.1f}%")
    
    print("\n Modos de Operação:")
    print("-" * 70)
    modes = [s['mode'] for s in SCIENTIFIC_SCENARIOS]
    mode_counts = Counter(modes)
    for mode, count in sorted(mode_counts.items()):
        print(f"  {mode:20s}: {count:3d} cenários")
    
    print("="*70)


if __name__ == "__main__":
    print_scenario_summary()
    
    # Mostra primeiros 5 de cada categoria
    from collections import defaultdict
    by_category = defaultdict(list)
    for s in SCIENTIFIC_SCENARIOS:
        by_category[s['category']].append(s)
    
    print("\n Exemplos por Categoria (primeiros 3):")
    print("="*70)
    for cat in sorted(by_category.keys()):
        print(f"\n{cat.upper()}:")
        for s in by_category[cat][:3]:
            print(f"  • {s['scenario_id']:30s} - {s['description']}")
