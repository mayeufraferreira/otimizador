from src.models.region import Region
from src.models.workload import Workload

def check_hard_constraints(region: Region, workload: Workload):
    # Valida se a região atende aos hard constraints (requisitos obrigatórios) (requisitos obrigatórios)
    violations = []

    # Latência não pode exceder o limite definido no workload
    if region.avg_latency_ms > workload.latency_threshold_ms:
        violations.append(f"Error: Latency ({region.avg_latency_ms}ms) above threshold ({workload.latency_threshold_ms}ms)")

    # Capacidade de CPU deve ser 20% superior à necessária (margem de segurança)
    if region.cpu_available < workload.cpu_required * 1.2:
        violations.append(f"Error: Insufficient CPU (available: {region.cpu_available}, required: {workload.cpu_required * 1.2})")

    # Região tem que estar ativa
    if region.status != "active":
        violations.append(f"Inactive region: {region.name}")

    passed = len(violations) == 0
    return passed, violations
