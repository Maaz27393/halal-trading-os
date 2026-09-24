class ResourceUtilizationAnalyzer:
    """
    Evaluates system resource utilization (CPU, memory, queue saturation, API throughput).
    """
    def analyze_utilization(self, cpu_pct: float, memory_pct: float, queue_length: int) -> dict:
        saturation_score = round((cpu_pct * 0.4) + (memory_pct * 0.4) + (min(queue_length / 100.0, 1.0) * 20.0), 2)
        status = "HEALTHY" if saturation_score < 70.0 else ("ELEVATED" if saturation_score < 90.0 else "SATURATED")
        
        return {
            "cpu_utilization_pct": cpu_pct,
            "memory_utilization_pct": memory_pct,
            "queue_length": queue_length,
            "saturation_score": saturation_score,
            "status": status
        }
