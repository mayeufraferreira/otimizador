from dataclasses import dataclass
from typing import Optional

@dataclass
class Workload:
    # Representa uma carga de trabalho a ser orquestrada
    id: str
    cpu_required: int  # Quantidade de CPUs necessária
    priority: str  # Prioridade: 'high', 'medium', 'low'
    current_region: Optional[str] = None  # Região atual (opcional)
    latency_threshold_ms: float = 2000.0  # Latência máxima aceitável em ms

    def __post_init__(self):
        if self.cpu_required < 0:
            raise ValueError(f"cpu_required cannot be negative")
        if self.latency_threshold_ms < 0:
            raise ValueError(f"latency_threshold_ms cannot be negative")
        if self.priority not in ['high', 'medium', 'low']:
            raise ValueError(f"Invalid priority: {self.priority}")
