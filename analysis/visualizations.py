"""
Geração de gráficos e visualizações dos resultados do otimizador de workloads
Cria visualizações completas por modo, cenário, região, métricas e intervalos de confiança
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats
import sys
import os

# Adiciona diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Configurações de estilo
sns.set_style("whitegrid")
sns.set_context("notebook", font_scale=1.1)
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'

# Paleta de cores consistente
COLORS = {
    'balanced': '#2E86AB',
    'sustainable': '#06A77D',
    'emergency_latency': '#D62839',
    'emergency_cost': '#F77F00'
}

METRIC_COLORS = {
    'latency': '#E63946',
    'carbon': '#06A77D',
    'renewable': '#06A77D',
    'cost': '#F77F00',
    'score': '#2E86AB'
}


def load_data(csv_file: str) -> pd.DataFrame:
    """
    Carrega os dados de resultados
    
    Args:
        csv_file: Caminho para o arquivo CSV com os resultados
    
    Returns:
        DataFrame com os dados carregados
    """
    if not Path(csv_file).exists():
        raise FileNotFoundError(f"❌ Arquivo não encontrado: {csv_file}")
    
    df = pd.read_csv(csv_file)
    print(f"✅ {len(df):,} registros carregados de {csv_file}")
    return df


def calculate_confidence_interval(data: pd.Series, confidence: float = 0.95):
    """
    Calcula o intervalo de confiança para uma série de dados
    
    Args:
        data: Série de dados
        confidence: Nível de confiança (padrão: 0.95)
    
    Returns:
        Tupla com (média, erro_inferior, erro_superior)
    """
    n = len(data)
    mean = data.mean()
    std_err = stats.sem(data)
    
    # Intervalo de confiança usando distribuição t-Student
    ci = std_err * stats.t.ppf((1 + confidence) / 2, n - 1)
    
    return mean, ci, ci


def plot_modes_comparison_metrics(df: pd.DataFrame, output_dir: str):
    """
    Gráfico comparativo de todas as métricas por modo operacional
    """
    print("📊 Gerando gráficos de comparação de métricas por modo...")
    
    # Filtra apenas alocações bem-sucedidas
    df_success = df[df['allocation_success'] == True].copy()
    
    # Agrupa por modo
    modes = df_success['mode'].unique()
    
    # Métricas para comparar
    metrics = {
        'Latência (ms)': 'region_latency_ms',
        'Energia Renovável (%)': 'region_renewable_pct',
        'Carbono (gCO2/kWh)': 'region_carbon_intensity',
        'Custo ($/kWh)': 'region_cost_per_kwh',
        'Score Final': 'score_final'
    }
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()
    
    for idx, (metric_name, metric_col) in enumerate(metrics.items()):
        ax = axes[idx]
        
        # Prepara dados para cada modo
        data_by_mode = []
        labels = []
        colors_list = []
        
        for mode in sorted(modes):
            mode_data = df_success[df_success['mode'] == mode][metric_col].dropna()
            if len(mode_data) > 0:
                data_by_mode.append(mode_data)
                labels.append(mode.replace('_', '\n'))
                colors_list.append(COLORS.get(mode, '#666666'))
        
        # Box plot
        bp = ax.boxplot(data_by_mode, tick_labels=labels, patch_artist=True,
                        showmeans=True, meanline=True)
        
        # Colorir as caixas
        for patch, color in zip(bp['boxes'], colors_list):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_title(metric_name, fontsize=14, fontweight='bold')
        ax.set_ylabel('Valor', fontsize=11)
        ax.grid(True, alpha=0.3)
        
        # Adiciona valores médios
        for i, data in enumerate(data_by_mode):
            mean_val = data.mean()
            ax.text(i + 1, mean_val, f'{mean_val:.2f}',
                   ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # Remove o último subplot vazio
    fig.delaxes(axes[-1])
    
    plt.suptitle('Comparação de Métricas por Modo Operacional', 
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    output_path = Path(output_dir) / 'comparison_modes_metrics_boxplot.png'
    plt.savefig(output_path)
    print(f"   ✅ Salvo: {output_path}")
    plt.close()


def plot_modes_comparison_with_ci(df: pd.DataFrame, output_dir: str):
    """
    Gráfico de comparação entre modos com intervalos de confiança
    """
    print("📊 Gerando gráficos de comparação de modos com intervalos de confiança...")
    
    df_success = df[df['allocation_success'] == True].copy()
    
    metrics = {
        'Latência (ms)': 'region_latency_ms',
        'Renovável (%)': 'region_renewable_pct',
        'Carbono (gCO2)': 'region_carbon_intensity',
        'Custo ($/kWh)': 'region_cost_per_kwh'
    }
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()
    
    for idx, (metric_name, metric_col) in enumerate(metrics.items()):
        ax = axes[idx]
        
        # Calcula estatísticas por modo
        modes_data = []
        for mode in sorted(df_success['mode'].unique()):
            mode_df = df_success[df_success['mode'] == mode]
            data = mode_df[metric_col].dropna()
            
            if len(data) > 0:
                mean, ci_lower, ci_upper = calculate_confidence_interval(data)
                modes_data.append({
                    'mode': mode,
                    'mean': mean,
                    'ci_lower': ci_lower,
                    'ci_upper': ci_upper
                })
        
        # Plota barras com intervalos de confiança
        x_pos = np.arange(len(modes_data))
        means = [d['mean'] for d in modes_data]
        ci_lowers = [d['ci_lower'] for d in modes_data]
        ci_uppers = [d['ci_upper'] for d in modes_data]
        labels = [d['mode'].replace('_', '\n') for d in modes_data]
        colors_list = [COLORS.get(d['mode'], '#666666') for d in modes_data]
        
        bars = ax.bar(x_pos, means, yerr=[ci_lowers, ci_uppers],
                     capsize=10, color=colors_list, alpha=0.7,
                     error_kw={'linewidth': 2, 'elinewidth': 2})
        
        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels, fontsize=10)
        ax.set_title(metric_name, fontsize=14, fontweight='bold')
        ax.set_ylabel('Valor Médio', fontsize=11)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Adiciona valores nas barras
        for i, (bar, mean) in enumerate(zip(bars, means)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{mean:.2f}',
                   ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.suptitle('Comparação de Modos com Intervalos de Confiança (95%)',
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    output_path = Path(output_dir) / 'comparison_modes_confidence_intervals.png'
    plt.savefig(output_path)
    print(f"   ✅ Salvo: {output_path}")
    plt.close()


def plot_scores_by_mode(df: pd.DataFrame, output_dir: str):
    """
    Gráfico de scores individuais e final por modo
    """
    print("📊 Gerando gráficos de scores por modo...")
    
    df_success = df[df['allocation_success'] == True].copy()
    
    # Scores para analisar
    score_cols = ['score_latency', 'score_carbon', 'score_cost', 'score_final']
    score_labels = ['Latência', 'Carbono', 'Custo', 'Final']
    
    modes = sorted(df_success['mode'].unique())
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()
    
    for idx, (score_col, score_label) in enumerate(zip(score_cols, score_labels)):
        ax = axes[idx]
        
        # Dados por modo
        data_by_mode = []
        labels = []
        colors_list = []
        
        for mode in modes:
            mode_data = df_success[df_success['mode'] == mode][score_col].dropna()
            if len(mode_data) > 0:
                data_by_mode.append(mode_data)
                labels.append(mode.replace('_', '\n'))
                colors_list.append(COLORS.get(mode, '#666666'))
        
        # Violin plot para mostrar distribuição
        parts = ax.violinplot(data_by_mode, positions=range(len(data_by_mode)),
                             showmeans=True, showmedians=True)
        
        # Colorir os violinos
        for i, pc in enumerate(parts['bodies']):
            pc.set_facecolor(colors_list[i])
            pc.set_alpha(0.7)
        
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, fontsize=10)
        ax.set_title(f'Score de {score_label}', fontsize=14, fontweight='bold')
        ax.set_ylabel('Score (0-1)', fontsize=11)
        ax.set_ylim(0, 1.05)
        ax.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('Distribuição de Scores por Modo Operacional',
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    output_path = Path(output_dir) / 'scores_by_mode_violin.png'
    plt.savefig(output_path)
    print(f"   ✅ Salvo: {output_path}")
    plt.close()


def plot_metrics_separated(df: pd.DataFrame, output_dir: str):
    """
    Gráficos individuais para cada métrica (1 gráfico por métrica)
    """
    print("📊 Gerando gráficos separados por métrica...")
    
    df_success = df[df['allocation_success'] == True].copy()
    modes = sorted(df_success['mode'].unique())
    
    metrics_config = [
        ('region_latency_ms', 'Latência (ms)', 'latency', False),
        ('region_renewable_pct', 'Energia Renovável (%)', 'renewable', True),
        ('region_carbon_intensity', 'Intensidade de Carbono (gCO2/kWh)', 'carbon', False),
        ('region_cost_per_kwh', 'Custo de Energia ($/kWh)', 'cost', False),
        ('score_final', 'Score Final', 'score', True)
    ]
    
    for metric_col, metric_name, metric_key, higher_better in metrics_config:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Subplot 1: Distribuição (box plot)
        data_by_mode = []
        labels = []
        colors_list = []
        
        for mode in modes:
            mode_data = df_success[df_success['mode'] == mode][metric_col].dropna()
            if len(mode_data) > 0:
                data_by_mode.append(mode_data)
                labels.append(mode.replace('_', '\n'))
                colors_list.append(COLORS.get(mode, '#666666'))
        
        bp = ax1.boxplot(data_by_mode, tick_labels=labels, patch_artist=True,
                        showmeans=True, meanline=True)
        
        for patch, color in zip(bp['boxes'], colors_list):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax1.set_title(f'Distribuição - {metric_name}', fontsize=13, fontweight='bold')
        ax1.set_ylabel('Valor', fontsize=11)
        ax1.grid(True, alpha=0.3)
        
        # Subplot 2: Média com intervalo de confiança
        modes_stats = []
        for mode in modes:
            mode_data = df_success[df_success['mode'] == mode][metric_col].dropna()
            if len(mode_data) > 0:
                mean, ci_lower, ci_upper = calculate_confidence_interval(mode_data)
                modes_stats.append({
                    'mode': mode,
                    'mean': mean,
                    'ci_lower': ci_lower,
                    'ci_upper': ci_upper
                })
        
        x_pos = np.arange(len(modes_stats))
        means = [s['mean'] for s in modes_stats]
        errors_lower = [s['ci_lower'] for s in modes_stats]
        errors_upper = [s['ci_upper'] for s in modes_stats]
        stat_labels = [s['mode'].replace('_', '\n') for s in modes_stats]
        stat_colors = [COLORS.get(s['mode'], '#666666') for s in modes_stats]
        
        bars = ax2.bar(x_pos, means, yerr=[errors_lower, errors_upper],
                      capsize=10, color=stat_colors, alpha=0.7,
                      error_kw={'linewidth': 2})
        
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(stat_labels, fontsize=10)
        ax2.set_title(f'Média com IC 95% - {metric_name}', fontsize=13, fontweight='bold')
        ax2.set_ylabel('Valor Médio', fontsize=11)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Adiciona valores
        for bar, mean in zip(bars, means):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{mean:.2f}',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # Indica se maior é melhor
        direction = "↑ Maior é melhor" if higher_better else "↓ Menor é melhor"
        fig.text(0.5, 0.02, direction, ha='center', fontsize=11, 
                style='italic', color='gray')
        
        plt.suptitle(f'Análise de {metric_name}',
                    fontsize=15, fontweight='bold')
        plt.tight_layout(rect=[0, 0.03, 1, 0.97])
        
        # Nome do arquivo
        filename = metric_key.replace(' ', '_').lower()
        output_path = Path(output_dir) / f'metric_{filename}_detailed.png'
        plt.savefig(output_path)
        print(f"   ✅ Salvo: {output_path}")
        plt.close()


def plot_scenarios_analysis(df: pd.DataFrame, output_dir: str):
    """
    Análise por cenários científicos
    """
    print("📊 Gerando gráficos de análise por cenários...")
    
    if 'scenario_category' not in df.columns:
        print("   ⚠️  Coluna 'scenario_category' não encontrada. Pulando...")
        return
    
    df_success = df[df['allocation_success'] == True].copy()
    
    # Agrupa por categoria de cenário
    categories = df_success['scenario_category'].unique()
    
    if len(categories) == 0:
        print("   ⚠️  Nenhuma categoria de cenário encontrada. Pulando...")
        return
    
    # Score final por categoria de cenário
    fig, ax = plt.subplots(figsize=(14, 8))
    
    category_data = []
    category_labels = []
    
    for category in sorted(categories):
        cat_data = df_success[df_success['scenario_category'] == category]['score_final'].dropna()
        if len(cat_data) > 0:
            category_data.append(cat_data)
            category_labels.append(category.replace('_', '\n'))
    
    bp = ax.boxplot(category_data, tick_labels=category_labels, patch_artist=True,
                   showmeans=True, meanline=True)
    
    # Colorir
    colors = plt.cm.Set3(np.linspace(0, 1, len(category_data)))
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax.set_title('Score Final por Categoria de Cenário', fontsize=15, fontweight='bold')
    ax.set_xlabel('Categoria do Cenário', fontsize=12)
    ax.set_ylabel('Score Final', fontsize=12)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3, axis='y')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    output_path = Path(output_dir) / 'scenarios_by_category.png'
    plt.savefig(output_path)
    print(f"   ✅ Salvo: {output_path}")
    plt.close()


def plot_variance_sensitivity(df: pd.DataFrame, output_dir: str):
    """
    Análise de sensibilidade à variância
    """
    print("📊 Gerando gráficos de sensibilidade à variância...")
    
    if 'variance' not in df.columns:
        print("   ⚠️  Coluna 'variance' não encontrada. Pulando...")
        return
    
    df_success = df[df['allocation_success'] == True].copy()
    
    # Agrupa por variância e calcula médias
    variance_stats = df_success.groupby('variance').agg({
        'score_final': ['mean', 'std', 'count'],
        'region_latency_ms': 'mean',
        'region_renewable_pct': 'mean',
        'region_cost_per_kwh': 'mean'
    }).reset_index()
    
    variance_stats.columns = ['_'.join(col).strip('_') for col in variance_stats.columns]
    variance_stats = variance_stats.sort_values('variance')
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Score final vs variância
    ax = axes[0, 0]
    ax.plot(variance_stats['variance'] * 100, variance_stats['score_final_mean'],
           marker='o', linewidth=2, markersize=8, color=METRIC_COLORS['score'])
    ax.fill_between(variance_stats['variance'] * 100,
                    variance_stats['score_final_mean'] - variance_stats['score_final_std'],
                    variance_stats['score_final_mean'] + variance_stats['score_final_std'],
                    alpha=0.3, color=METRIC_COLORS['score'])
    ax.set_title('Score Final vs Variância', fontsize=13, fontweight='bold')
    ax.set_xlabel('Variância (%)', fontsize=11)
    ax.set_ylabel('Score Final Médio', fontsize=11)
    ax.grid(True, alpha=0.3)
    
    # Latência vs variância
    ax = axes[0, 1]
    ax.plot(variance_stats['variance'] * 100, variance_stats['region_latency_ms_mean'],
           marker='s', linewidth=2, markersize=8, color=METRIC_COLORS['latency'])
    ax.set_title('Latência Média vs Variância', fontsize=13, fontweight='bold')
    ax.set_xlabel('Variância (%)', fontsize=11)
    ax.set_ylabel('Latência (ms)', fontsize=11)
    ax.grid(True, alpha=0.3)
    
    # Renovável vs variância
    ax = axes[1, 0]
    ax.plot(variance_stats['variance'] * 100, variance_stats['region_renewable_pct_mean'],
           marker='^', linewidth=2, markersize=8, color=METRIC_COLORS['renewable'])
    ax.set_title('Energia Renovável vs Variância', fontsize=13, fontweight='bold')
    ax.set_xlabel('Variância (%)', fontsize=11)
    ax.set_ylabel('Renovável (%)', fontsize=11)
    ax.grid(True, alpha=0.3)
    
    # Custo vs variância
    ax = axes[1, 1]
    ax.plot(variance_stats['variance'] * 100, variance_stats['region_cost_per_kwh_mean'],
           marker='d', linewidth=2, markersize=8, color=METRIC_COLORS['cost'])
    ax.set_title('Custo Médio vs Variância', fontsize=13, fontweight='bold')
    ax.set_xlabel('Variância (%)', fontsize=11)
    ax.set_ylabel('Custo ($/kWh)', fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.suptitle('Análise de Sensibilidade à Variância',
                fontsize=15, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    output_path = Path(output_dir) / 'sensitivity_variance.png'
    plt.savefig(output_path)
    print(f"   ✅ Salvo: {output_path}")
    plt.close()


def plot_region_selection_distribution(df: pd.DataFrame, output_dir: str):
    """
    Distribuição de seleção de regiões
    """
    print("📊 Gerando gráficos de distribuição de regiões...")
    
    df_success = df[df['allocation_success'] == True].copy()
    
    # Top 20 regiões mais selecionadas
    region_counts = df_success['best_region_id'].value_counts().head(20)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
    
    # Subplot 1: Barras horizontais
    ax1.barh(range(len(region_counts)), region_counts.values,
            color=plt.cm.viridis(np.linspace(0, 1, len(region_counts))))
    ax1.set_yticks(range(len(region_counts)))
    ax1.set_yticklabels(region_counts.index, fontsize=9)
    ax1.set_xlabel('Número de Seleções', fontsize=11)
    ax1.set_title('Top 20 Regiões Mais Selecionadas', fontsize=13, fontweight='bold')
    ax1.invert_yaxis()
    ax1.grid(True, alpha=0.3, axis='x')
    
    # Adiciona valores
    for i, v in enumerate(region_counts.values):
        ax1.text(v, i, f' {v}', va='center', fontsize=9)
    
    # Subplot 2: Distribuição por modo
    region_mode = df_success.groupby(['mode', 'best_region_id']).size().reset_index(name='count')
    top_regions = region_counts.head(10).index
    region_mode = region_mode[region_mode['best_region_id'].isin(top_regions)]
    
    pivot_data = region_mode.pivot(index='best_region_id', columns='mode', values='count').fillna(0)
    
    # Ordena por total
    pivot_data['total'] = pivot_data.sum(axis=1)
    pivot_data = pivot_data.sort_values('total', ascending=False).drop('total', axis=1)
    
    # Gráfico de barras empilhadas
    pivot_data.plot(kind='barh', stacked=True, ax=ax2,
                   color=[COLORS.get(mode, '#666666') for mode in pivot_data.columns])
    ax2.set_xlabel('Número de Seleções', fontsize=11)
    ax2.set_title('Top 10 Regiões por Modo Operacional', fontsize=13, fontweight='bold')
    ax2.legend(title='Modo', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax2.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    
    output_path = Path(output_dir) / 'region_selection_distribution.png'
    plt.savefig(output_path)
    print(f"   ✅ Salvo: {output_path}")
    plt.close()


def plot_workload_priority_analysis(df: pd.DataFrame, output_dir: str):
    """
    Análise por prioridade de workload
    """
    print("📊 Gerando gráficos de análise por prioridade de workload...")
    
    if 'workload_priority' not in df.columns:
        print("   ⚠️  Coluna 'workload_priority' não encontrada. Pulando...")
        return
    
    df_success = df[df['allocation_success'] == True].copy()
    
    priorities = sorted(df_success['workload_priority'].unique())
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()
    
    metrics = [
        ('score_final', 'Score Final', METRIC_COLORS['score']),
        ('region_latency_ms', 'Latência (ms)', METRIC_COLORS['latency']),
        ('region_renewable_pct', 'Renovável (%)', METRIC_COLORS['renewable']),
        ('region_cost_per_kwh', 'Custo ($/kWh)', METRIC_COLORS['cost'])
    ]
    
    for idx, (metric_col, metric_name, color) in enumerate(metrics):
        ax = axes[idx]
        
        priority_data = []
        priority_labels = []
        
        for priority in priorities:
            pri_data = df_success[df_success['workload_priority'] == priority][metric_col].dropna()
            if len(pri_data) > 0:
                priority_data.append(pri_data)
                priority_labels.append(str(priority))
        
        bp = ax.boxplot(priority_data, tick_labels=priority_labels, patch_artist=True,
                       showmeans=True, meanline=True)
        
        for patch in bp['boxes']:
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_title(f'{metric_name} por Prioridade', fontsize=13, fontweight='bold')
        ax.set_xlabel('Prioridade do Workload', fontsize=11)
        ax.set_ylabel(metric_name, fontsize=11)
        ax.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('Análise por Prioridade de Workload',
                fontsize=15, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    output_path = Path(output_dir) / 'workload_priority_analysis.png'
    plt.savefig(output_path)
    print(f"   ✅ Salvo: {output_path}")
    plt.close()


def plot_scale_analysis(df: pd.DataFrame, output_dir: str):
    """
    Análise de escalabilidade (regiões e workloads)
    """
    print("📊 Gerando gráficos de análise de escalabilidade...")
    
    if 'n_regions' not in df.columns or 'n_workloads' not in df.columns:
        print("   ⚠️  Colunas de escala não encontradas. Pulando...")
        return
    
    df_success = df[df['allocation_success'] == True].copy()
    
    fig, axes = plt.subplots(1, 2, figsize=(18, 7))
    
    # Escala de regiões
    if len(df_success['n_regions'].unique()) > 1:
        ax = axes[0]
        regions_stats = df_success.groupby('n_regions').agg({
            'score_final': ['mean', 'std'],
            'region_latency_ms': 'mean'
        }).reset_index()
        
        regions_stats.columns = ['_'.join(col).strip('_') for col in regions_stats.columns]
        regions_stats = regions_stats.sort_values('n_regions')
        
        ax.plot(regions_stats['n_regions'], regions_stats['score_final_mean'],
               marker='o', linewidth=2, markersize=8, color=METRIC_COLORS['score'],
               label='Score Final')
        ax.fill_between(regions_stats['n_regions'],
                       regions_stats['score_final_mean'] - regions_stats['score_final_std'],
                       regions_stats['score_final_mean'] + regions_stats['score_final_std'],
                       alpha=0.3, color=METRIC_COLORS['score'])
        
        ax.set_title('Escalabilidade: Número de Regiões', fontsize=13, fontweight='bold')
        ax.set_xlabel('Número de Regiões', fontsize=11)
        ax.set_ylabel('Score Final Médio', fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.legend()
    
    # Escala de workloads
    if len(df_success['n_workloads'].unique()) > 1:
        ax = axes[1]
        workloads_stats = df_success.groupby('n_workloads').agg({
            'score_final': ['mean', 'std']
        }).reset_index()
        
        workloads_stats.columns = ['_'.join(col).strip('_') for col in workloads_stats.columns]
        workloads_stats = workloads_stats.sort_values('n_workloads')
        
        ax.plot(workloads_stats['n_workloads'], workloads_stats['score_final_mean'],
               marker='s', linewidth=2, markersize=8, color=METRIC_COLORS['cost'],
               label='Score Final')
        ax.fill_between(workloads_stats['n_workloads'],
                       workloads_stats['score_final_mean'] - workloads_stats['score_final_std'],
                       workloads_stats['score_final_mean'] + workloads_stats['score_final_std'],
                       alpha=0.3, color=METRIC_COLORS['cost'])
        
        ax.set_title('Escalabilidade: Número de Workloads', fontsize=13, fontweight='bold')
        ax.set_xlabel('Número de Workloads', fontsize=11)
        ax.set_ylabel('Score Final Médio', fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.legend()
    
    plt.suptitle('Análise de Escalabilidade',
                fontsize=15, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    output_path = Path(output_dir) / 'scale_analysis.png'
    plt.savefig(output_path)
    print(f"   ✅ Salvo: {output_path}")
    plt.close()


def plot_correlation_heatmap(df: pd.DataFrame, output_dir: str):
    """
    Mapa de calor de correlações entre métricas
    """
    print("📊 Gerando mapa de calor de correlações...")
    
    df_success = df[df['allocation_success'] == True].copy()
    
    # Seleciona colunas numéricas relevantes
    correlation_cols = [
        'region_latency_ms', 'region_renewable_pct', 
        'region_carbon_intensity', 'region_cost_per_kwh',
        'score_latency', 'score_carbon', 'score_cost', 'score_final'
    ]
    
    # Filtra apenas colunas que existem
    correlation_cols = [col for col in correlation_cols if col in df_success.columns]
    
    if len(correlation_cols) < 2:
        print("   ⚠️  Colunas insuficientes para correlação. Pulando...")
        return
    
    # Calcula correlação
    corr_matrix = df_success[correlation_cols].corr()
    
    # Renomeia para labels mais legíveis
    label_map = {
        'region_latency_ms': 'Latência',
        'region_renewable_pct': 'Renovável %',
        'region_carbon_intensity': 'Carbono',
        'region_cost_per_kwh': 'Custo',
        'score_latency': 'Score Lat.',
        'score_carbon': 'Score Carb.',
        'score_cost': 'Score Custo',
        'score_final': 'Score Final'
    }
    
    corr_matrix.index = [label_map.get(col, col) for col in corr_matrix.index]
    corr_matrix.columns = [label_map.get(col, col) for col in corr_matrix.columns]
    
    # Plota
    fig, ax = plt.subplots(figsize=(12, 10))
    
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm',
                center=0, vmin=-1, vmax=1, square=True,
                linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
    
    ax.set_title('Correlação entre Métricas e Scores', 
                fontsize=15, fontweight='bold', pad=20)
    
    plt.tight_layout()
    
    output_path = Path(output_dir) / 'correlation_heatmap.png'
    plt.savefig(output_path)
    print(f"   ✅ Salvo: {output_path}")
    plt.close()


def plot_success_rate_analysis(df: pd.DataFrame, output_dir: str):
    """
    Análise de taxa de sucesso de alocações
    """
    print("📊 Gerando gráficos de taxa de sucesso...")
    
    # Taxa de sucesso por modo
    mode_success = df.groupby('mode').agg({
        'allocation_success': ['sum', 'count']
    }).reset_index()
    
    mode_success.columns = ['mode', 'success', 'total']
    mode_success['rate'] = (mode_success['success'] / mode_success['total']) * 100
    mode_success = mode_success.sort_values('rate', ascending=False)
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    colors_list = [COLORS.get(mode, '#666666') for mode in mode_success['mode']]
    
    bars = ax.bar(range(len(mode_success)), mode_success['rate'],
                 color=colors_list, alpha=0.7)
    
    ax.set_xticks(range(len(mode_success)))
    ax.set_xticklabels([mode.replace('_', '\n') for mode in mode_success['mode']], fontsize=11)
    ax.set_ylabel('Taxa de Sucesso (%)', fontsize=12)
    ax.set_title('Taxa de Sucesso de Alocação por Modo Operacional',
                fontsize=15, fontweight='bold')
    ax.set_ylim(0, 105)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Adiciona valores e counts
    for i, (bar, row) in enumerate(zip(bars, mode_success.itertuples())):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{row.rate:.1f}%\n({row.success}/{row.total})',
               ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    
    output_path = Path(output_dir) / 'success_rate_by_mode.png'
    plt.savefig(output_path)
    print(f"   ✅ Salvo: {output_path}")
    plt.close()


def plot_metrics_by_region(df: pd.DataFrame, output_dir: str):
    """
    Análise de métricas por região individual
    """
    print("📊 Gerando gráficos de análise por região...")
    
    df_success = df[df['allocation_success'] == True].copy()
    
    if 'best_region_id' not in df_success.columns:
        print("   ⚠️  Coluna 'best_region_id' não encontrada. Pulando...")
        return
    
    # Agrupa por região e calcula estatísticas
    region_stats = df_success.groupby('best_region_id').agg({
        'region_latency_ms': ['mean', 'std', 'count'],
        'region_cost_per_kwh': ['mean', 'std'],
        'region_renewable_pct': ['mean', 'std'],
        'region_carbon_intensity': ['mean', 'std']
    }).reset_index()
    
    region_stats.columns = ['_'.join(col).strip('_') for col in region_stats.columns]
    
    # Filtra regiões com pelo menos 10 seleções
    region_stats = region_stats[region_stats['region_latency_ms_count'] >= 10]
    region_stats = region_stats.sort_values('region_latency_ms_count', ascending=False).head(20)
    
    if len(region_stats) == 0:
        print("   ⚠️  Dados insuficientes por região. Pulando...")
        return
    
    # Cria 3 subplots
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    
    # Subplot 1: Latência por região
    ax = axes[0]
    region_stats_sorted = region_stats.sort_values('region_latency_ms_mean')
    
    bars = ax.barh(range(len(region_stats_sorted)), 
                   region_stats_sorted['region_latency_ms_mean'],
                   xerr=region_stats_sorted['region_latency_ms_std'],
                   color=METRIC_COLORS['latency'], alpha=0.7, capsize=5)
    
    ax.set_yticks(range(len(region_stats_sorted)))
    ax.set_yticklabels(region_stats_sorted['best_region_id'], fontsize=9)
    ax.set_xlabel('Latência Média (ms)', fontsize=11)
    ax.set_title('Latência por Região (Top 20)', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    ax.invert_yaxis()
    
    # Subplot 2: Custo por região
    ax = axes[1]
    region_stats_sorted = region_stats.sort_values('region_cost_per_kwh_mean')
    
    bars = ax.barh(range(len(region_stats_sorted)), 
                   region_stats_sorted['region_cost_per_kwh_mean'],
                   xerr=region_stats_sorted['region_cost_per_kwh_std'],
                   color=METRIC_COLORS['cost'], alpha=0.7, capsize=5)
    
    ax.set_yticks(range(len(region_stats_sorted)))
    ax.set_yticklabels(region_stats_sorted['best_region_id'], fontsize=9)
    ax.set_xlabel('Custo Médio ($/kWh)', fontsize=11)
    ax.set_title('Custo por Região (Top 20)', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    ax.invert_yaxis()
    
    # Subplot 3: Sustentabilidade por região
    ax = axes[2]
    region_stats_sorted = region_stats.sort_values('region_renewable_pct_mean', ascending=False)
    
    bars = ax.barh(range(len(region_stats_sorted)), 
                   region_stats_sorted['region_renewable_pct_mean'],
                   xerr=region_stats_sorted['region_renewable_pct_std'],
                   color=METRIC_COLORS['renewable'], alpha=0.7, capsize=5)
    
    ax.set_yticks(range(len(region_stats_sorted)))
    ax.set_yticklabels(region_stats_sorted['best_region_id'], fontsize=9)
    ax.set_xlabel('Energia Renovável Média (%)', fontsize=11)
    ax.set_title('Sustentabilidade por Região (Top 20)', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    ax.invert_yaxis()
    
    plt.suptitle('Análise de Métricas por Região', fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    output_path = Path(output_dir) / 'metrics_by_region.png'
    plt.savefig(output_path)
    print(f"   ✅ Salvo: {output_path}")
    plt.close()


def plot_tradeoffs_scatter(df: pd.DataFrame, output_dir: str):
    """
    Gráficos de trade-off entre métricas (scatter plots)
    """
    print("📊 Gerando gráficos de trade-offs entre métricas...")
    
    df_success = df[df['allocation_success'] == True].copy()
    
    # Amostra para melhor visualização se dataset muito grande
    if len(df_success) > 5000:
        df_plot = df_success.sample(n=5000, random_state=42)
    else:
        df_plot = df_success
    
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    
    # Subplot 1: Latência vs Sustentabilidade
    ax = axes[0]
    for mode in sorted(df_plot['mode'].unique()):
        mode_data = df_plot[df_plot['mode'] == mode]
        ax.scatter(mode_data['region_latency_ms'], 
                  mode_data['region_renewable_pct'],
                  alpha=0.5, s=30, label=mode.replace('_', ' ').title(),
                  color=COLORS.get(mode, '#666666'))
    
    ax.set_xlabel('Latência (ms)', fontsize=11)
    ax.set_ylabel('Energia Renovável (%)', fontsize=11)
    ax.set_title('Trade-off: Latência vs Sustentabilidade', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9, loc='best')
    
    # Subplot 2: Latência vs Custo
    ax = axes[1]
    for mode in sorted(df_plot['mode'].unique()):
        mode_data = df_plot[df_plot['mode'] == mode]
        ax.scatter(mode_data['region_latency_ms'], 
                  mode_data['region_cost_per_kwh'],
                  alpha=0.5, s=30, label=mode.replace('_', ' ').title(),
                  color=COLORS.get(mode, '#666666'))
    
    ax.set_xlabel('Latência (ms)', fontsize=11)
    ax.set_ylabel('Custo ($/kWh)', fontsize=11)
    ax.set_title('Trade-off: Latência vs Custo', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9, loc='best')
    
    # Subplot 3: Custo vs Sustentabilidade
    ax = axes[2]
    for mode in sorted(df_plot['mode'].unique()):
        mode_data = df_plot[df_plot['mode'] == mode]
        ax.scatter(mode_data['region_cost_per_kwh'], 
                  mode_data['region_renewable_pct'],
                  alpha=0.5, s=30, label=mode.replace('_', ' ').title(),
                  color=COLORS.get(mode, '#666666'))
    
    ax.set_xlabel('Custo ($/kWh)', fontsize=11)
    ax.set_ylabel('Energia Renovável (%)', fontsize=11)
    ax.set_title('Trade-off: Custo vs Sustentabilidade', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9, loc='best')
    
    plt.suptitle('Análise de Trade-offs entre Métricas', fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    output_path = Path(output_dir) / 'tradeoffs_scatter.png'
    plt.savefig(output_path)
    print(f"   ✅ Salvo: {output_path}")
    plt.close()


def plot_metrics_by_scenario_with_ci(df: pd.DataFrame, output_dir: str):
    """
    Distribuição de métricas por cenário com intervalos de confiança
    """
    print("📊 Gerando gráficos de métricas por cenário com IC...")
    
    if 'scenario_category' not in df.columns:
        print("   ⚠️  Coluna 'scenario_category' não encontrada. Pulando...")
        return
    
    df_success = df[df['allocation_success'] == True].copy()
    
    categories = sorted(df_success['scenario_category'].unique())
    
    if len(categories) == 0:
        print("   ⚠️  Nenhuma categoria de cenário encontrada. Pulando...")
        return
    
    # Calcula estatísticas por categoria
    metrics = [
        ('region_latency_ms', 'Latência (ms)', 'latency', False),
        ('region_cost_per_kwh', 'Custo ($/kWh)', 'cost', False),
        ('region_renewable_pct', 'Energia Renovável (%)', 'renewable', True)
    ]
    
    fig, axes = plt.subplots(1, 3, figsize=(20, 7))
    
    for idx, (metric_col, metric_name, metric_key, higher_better) in enumerate(metrics):
        ax = axes[idx]
        
        category_stats = []
        for category in categories:
            cat_data = df_success[df_success['scenario_category'] == category][metric_col].dropna()
            if len(cat_data) > 0:
                mean, ci_lower, ci_upper = calculate_confidence_interval(cat_data)
                category_stats.append({
                    'category': category,
                    'mean': mean,
                    'ci_lower': ci_lower,
                    'ci_upper': ci_upper
                })
        
        if len(category_stats) == 0:
            continue
        
        # Ordena por média
        category_stats = sorted(category_stats, key=lambda x: x['mean'], reverse=higher_better)
        
        x_pos = np.arange(len(category_stats))
        means = [s['mean'] for s in category_stats]
        ci_lowers = [s['ci_lower'] for s in category_stats]
        ci_uppers = [s['ci_upper'] for s in category_stats]
        labels = [s['category'].replace('_', '\n') for s in category_stats]
        
        bars = ax.bar(x_pos, means, yerr=[ci_lowers, ci_uppers],
                     capsize=8, color=METRIC_COLORS[metric_key], alpha=0.7,
                     error_kw={'linewidth': 2, 'elinewidth': 2})
        
        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
        ax.set_ylabel(metric_name, fontsize=11)
        ax.set_title(f'{metric_name} por Cenário', fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Adiciona valores
        for bar, mean in zip(bars, means):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{mean:.2f}',
                   ha='center', va='bottom', fontsize=8)
    
    plt.suptitle('Distribuição de Métricas por Categoria de Cenário (IC 95%)',
                fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    output_path = Path(output_dir) / 'metrics_by_scenario_ci.png'
    plt.savefig(output_path)
    print(f"   ✅ Salvo: {output_path}")
    plt.close()


def plot_doe_factorial_analysis(df: pd.DataFrame, output_dir: str):
    """
    Análise DoE (Design of Experiments) / Análise Fatorial Completa
    Analisa os efeitos principais e interações entre fatores
    """
    print("📊 Gerando análise DoE (Design of Experiments)...")
    
    df_success = df[df['allocation_success'] == True].copy()
    
    # Verifica se temos os fatores necessários
    required_cols = ['mode', 'variance']
    if not all(col in df_success.columns for col in required_cols):
        print("   ⚠️  Colunas necessárias para DoE não encontradas. Pulando...")
        return
    
    # Preparar dados categóricos
    # Codifica modo como numérico para análise
    mode_mapping = {mode: idx for idx, mode in enumerate(sorted(df_success['mode'].unique()))}
    df_success['mode_coded'] = df_success['mode'].map(mode_mapping)
    
    # Cria figura com 6 subplots
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # 1. Efeito Principal: Modo Operacional
    ax1 = fig.add_subplot(gs[0, 0])
    mode_effects = df_success.groupby('mode')['score_final'].agg(['mean', 'std', 'count']).reset_index()
    mode_effects = mode_effects.sort_values('mean', ascending=False)
    
    colors_list = [COLORS.get(mode, '#666666') for mode in mode_effects['mode']]
    bars = ax1.bar(range(len(mode_effects)), mode_effects['mean'],
                   yerr=mode_effects['std'], capsize=5, color=colors_list, alpha=0.7)
    ax1.set_xticks(range(len(mode_effects)))
    ax1.set_xticklabels([m.replace('_', '\n') for m in mode_effects['mode']], fontsize=9)
    ax1.set_ylabel('Score Final Médio', fontsize=10)
    ax1.set_title('Efeito Principal: Modo Operacional', fontsize=11, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # 2. Efeito Principal: Variância
    ax2 = fig.add_subplot(gs[0, 1])
    
    # Discretiza variância em bins
    df_success['variance_bin'] = pd.cut(df_success['variance'], bins=5)
    variance_effects = df_success.groupby('variance_bin', observed=True)['score_final'].agg(['mean', 'std', 'count']).reset_index()
    
    ax2.plot(range(len(variance_effects)), variance_effects['mean'], 
            marker='o', linewidth=2, markersize=8, color=METRIC_COLORS['score'])
    ax2.fill_between(range(len(variance_effects)),
                     variance_effects['mean'] - variance_effects['std'],
                     variance_effects['mean'] + variance_effects['std'],
                     alpha=0.3, color=METRIC_COLORS['score'])
    ax2.set_xticks(range(len(variance_effects)))
    ax2.set_xticklabels([f'{v.left:.1f} to\n{v.right:.1f}' for v in variance_effects['variance_bin']], 
                        fontsize=8)
    ax2.set_ylabel('Score Final Médio', fontsize=10)
    ax2.set_xlabel('Faixa de Variância', fontsize=10)
    ax2.set_title('Efeito Principal: Variância', fontsize=11, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # 3. Efeito Principal: N Regions (se disponível)
    ax3 = fig.add_subplot(gs[0, 2])
    if 'n_regions' in df_success.columns and len(df_success['n_regions'].unique()) > 1:
        region_effects = df_success.groupby('n_regions')['score_final'].agg(['mean', 'std', 'count']).reset_index()
        region_effects = region_effects.sort_values('n_regions')
        
        ax3.plot(region_effects['n_regions'], region_effects['mean'],
                marker='s', linewidth=2, markersize=8, color=METRIC_COLORS['cost'])
        ax3.fill_between(region_effects['n_regions'],
                        region_effects['mean'] - region_effects['std'],
                        region_effects['mean'] + region_effects['std'],
                        alpha=0.3, color=METRIC_COLORS['cost'])
        ax3.set_xlabel('Número de Regiões', fontsize=10)
        ax3.set_ylabel('Score Final Médio', fontsize=10)
        ax3.set_title('Efeito Principal: Número de Regiões', fontsize=11, fontweight='bold')
        ax3.grid(True, alpha=0.3)
    else:
        ax3.text(0.5, 0.5, 'Dados não disponíveis', ha='center', va='center', fontsize=10)
        ax3.set_title('Efeito Principal: N Regiões', fontsize=11, fontweight='bold')
    
    # 4. Interação: Modo × Variância
    ax4 = fig.add_subplot(gs[1, :2])
    
    # Cria pivot table para interação
    interaction_data = df_success.groupby(['mode', 'variance_bin'], observed=True)['score_final'].mean().reset_index()
    pivot_interaction = interaction_data.pivot(index='variance_bin', columns='mode', values='score_final')
    
    for mode in pivot_interaction.columns:
        ax4.plot(range(len(pivot_interaction)), pivot_interaction[mode],
                marker='o', linewidth=2, markersize=6, label=mode.replace('_', ' ').title(),
                color=COLORS.get(mode, '#666666'))
    
    ax4.set_xticks(range(len(pivot_interaction)))
    ax4.set_xticklabels([f'{v.left:.1f}-{v.right:.1f}' for v in pivot_interaction.index], fontsize=9)
    ax4.set_xlabel('Faixa de Variância', fontsize=10)
    ax4.set_ylabel('Score Final Médio', fontsize=10)
    ax4.set_title('Interação: Modo × Variância', fontsize=11, fontweight='bold')
    ax4.legend(fontsize=9, loc='best')
    ax4.grid(True, alpha=0.3)
    
    # 5. Heatmap de Interação: Modo × Variância
    ax5 = fig.add_subplot(gs[1, 2])
    
    # Prepara dados para heatmap
    heatmap_data = pivot_interaction.T
    
    sns.heatmap(heatmap_data, annot=True, fmt='.3f', cmap='RdYlGn',
                center=heatmap_data.mean().mean(), vmin=heatmap_data.min().min(),
                vmax=heatmap_data.max().max(), cbar_kws={'label': 'Score Final'},
                ax=ax5, linewidths=0.5)
    
    ax5.set_xlabel('Faixa de Variância', fontsize=10)
    ax5.set_ylabel('Modo Operacional', fontsize=10)
    ax5.set_title('Heatmap: Modo × Variância', fontsize=11, fontweight='bold')
    ax5.set_xticklabels([f'{v.left:.1f}-{v.right:.1f}' for v in pivot_interaction.index],
                        rotation=45, ha='right', fontsize=8)
    ax5.set_yticklabels([m.replace('_', ' ').title() for m in heatmap_data.index],
                        rotation=0, fontsize=9)
    
    # 6. Pareto de Efeitos (estimativa de importância)
    ax6 = fig.add_subplot(gs[2, :])
    
    # Calcula variância explicada por cada fator (R² parcial simplificado)
    effects = []
    
    # Efeito do modo
    mode_ss = df_success.groupby('mode')['score_final'].apply(
        lambda x: len(x) * (x.mean() - df_success['score_final'].mean())**2
    ).sum()
    effects.append(('Modo Operacional', mode_ss))
    
    # Efeito da variância
    variance_ss = df_success.groupby('variance_bin', observed=True)['score_final'].apply(
        lambda x: len(x) * (x.mean() - df_success['score_final'].mean())**2
    ).sum()
    effects.append(('Variância', variance_ss))
    
    # Efeito de n_regions (se disponível)
    if 'n_regions' in df_success.columns and len(df_success['n_regions'].unique()) > 1:
        regions_ss = df_success.groupby('n_regions')['score_final'].apply(
            lambda x: len(x) * (x.mean() - df_success['score_final'].mean())**2
        ).sum()
        effects.append(('N Regiões', regions_ss))
    
    # Efeito de n_workloads (se disponível)
    if 'n_workloads' in df_success.columns and len(df_success['n_workloads'].unique()) > 1:
        workloads_ss = df_success.groupby('n_workloads')['score_final'].apply(
            lambda x: len(x) * (x.mean() - df_success['score_final'].mean())**2
        ).sum()
        effects.append(('N Workloads', workloads_ss))
    
    # Ordena por importância
    effects = sorted(effects, key=lambda x: x[1], reverse=True)
    
    # Normaliza para porcentagem
    total_ss = sum([e[1] for e in effects])
    effects_pct = [(e[0], (e[1]/total_ss)*100) for e in effects]
    
    # Calcula efeito acumulado
    cumulative = np.cumsum([e[1] for e in effects_pct])
    
    # Plota Pareto
    x_pos = np.arange(len(effects_pct))
    bars = ax6.bar(x_pos, [e[1] for e in effects_pct], 
                   color=plt.cm.viridis(np.linspace(0, 1, len(effects_pct))), alpha=0.7)
    ax6.set_xticks(x_pos)
    ax6.set_xticklabels([e[0] for e in effects_pct], fontsize=10)
    ax6.set_ylabel('Importância (%)', fontsize=10)
    ax6.set_title('Diagrama de Pareto: Importância dos Fatores', fontsize=11, fontweight='bold')
    
    # Adiciona linha acumulada
    ax6_twin = ax6.twinx()
    ax6_twin.plot(x_pos, cumulative, color='red', marker='D', linewidth=2, markersize=6)
    ax6_twin.set_ylabel('Efeito Acumulado (%)', fontsize=10, color='red')
    ax6_twin.tick_params(axis='y', labelcolor='red')
    ax6_twin.set_ylim(0, 105)
    
    # Adiciona linha de 80%
    ax6_twin.axhline(y=80, color='red', linestyle='--', linewidth=1, alpha=0.5)
    ax6_twin.text(len(effects_pct)-0.5, 82, '80%', color='red', fontsize=9)
    
    # Adiciona valores nas barras
    for bar, (name, val) in zip(bars, effects_pct):
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.1f}%',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    ax6.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('Análise DoE (Design of Experiments) / Análise Fatorial',
                fontsize=16, fontweight='bold', y=0.995)
    
    output_path = Path(output_dir) / 'doe_factorial_analysis.png'
    plt.savefig(output_path)
    print(f"   ✅ Salvo: {output_path}")
    plt.close()


def generate_all_visualizations(csv_file: str, output_dir: str = "results/visualizations"):
    """
    Gera todas as visualizações
    
    Args:
        csv_file: Arquivo CSV com os resultados
        output_dir: Diretório de saída para os gráficos
    """
    print("\n" + "="*80)
    print("🎨 GERAÇÃO DE VISUALIZAÇÕES")
    print("="*80)
    
    # Cria diretório de saída
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    print(f"📁 Diretório de saída: {output_dir}\n")
    
    # Carrega dados
    df = load_data(csv_file)
    
    # Gera todos os gráficos
    plot_modes_comparison_metrics(df, output_dir)
    plot_modes_comparison_with_ci(df, output_dir)
    plot_scores_by_mode(df, output_dir)
    plot_metrics_separated(df, output_dir)
    plot_scenarios_analysis(df, output_dir)
    plot_variance_sensitivity(df, output_dir)
    plot_region_selection_distribution(df, output_dir)
    plot_workload_priority_analysis(df, output_dir)
    plot_scale_analysis(df, output_dir)
    plot_correlation_heatmap(df, output_dir)
    plot_success_rate_analysis(df, output_dir)
    
    # Novos gráficos adicionados
    plot_metrics_by_region(df, output_dir)
    plot_tradeoffs_scatter(df, output_dir)
    plot_metrics_by_scenario_with_ci(df, output_dir)
    plot_doe_factorial_analysis(df, output_dir)
    
    print("\n" + "="*80)
    print(f"✅ CONCLUÍDO! Todos os gráficos foram salvos em: {output_dir}")
    print("="*80)
    
    # Lista arquivos gerados
    generated_files = list(Path(output_dir).glob("*.png"))
    print(f"\n📊 Total de gráficos gerados: {len(generated_files)}")
    for file_path in sorted(generated_files):
        print(f"   • {file_path.name}")


def main():
    """Função principal"""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python visualizations.py <arquivo_csv> [diretorio_saida]")
        print("\nExemplo:")
        print("  python analysis/visualizations.py results/raw_results.csv")
        print("  python analysis/visualizations.py results/raw_results.csv results/graficos")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "results/visualizations"
    
    try:
        generate_all_visualizations(csv_file, output_dir)
    except Exception as e:
        print(f"\n❌ Erro ao gerar visualizações: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
