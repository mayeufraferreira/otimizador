from dataclasses import dataclass
from typing import Optional

@dataclass
class Region:
   # Representa um datacenter/região geográfica
   id: str
   name: str
   renewable_pct: float  # Porcentagem de energia renovável (0-100)
   carbon_intensity: float  # Intensidade de carbono em g/kWh
   cost_per_kwh: float  # Custo de energia por kWh
   cpu_available: int  # CPUs disponíveis na região
   avg_latency_ms: float  # Latência média em milissegundos
   status: str = 'active'  # Status da região (active/inactive)

   def __post_init__(self):
      if not (0 <= self.renewable_pct <= 100):
         raise ValueError(f"renewable_pct must be 0-100")
      if self.carbon_intensity < 0:
         raise ValueError(f"carbon_intensity cannot be negative")
      if self.cost_per_kwh < 0:
         raise ValueError(f"cost_per_kwh cannot be negative")
      if self.cpu_available < 0:
         raise ValueError(f"cpu_available cannot be negative")
      if self.avg_latency_ms < 0:
         raise ValueError(f"avg_latency_ms cannot be negative")
