import httpx
import os
from typing import Dict, Any

SIMULATOR_URL = os.getenv("SIMULATOR_URL", "http://localhost:8001")

def get_service_metrics(service: str) -> Dict[str, Any]:
    """
    Fetches the current metrics for a given service.
    Returns cpu, memory, error_rate, latency_p95, db_connections, request_rate, healthy status.
    """
    try:
        response = httpx.get(f"{SIMULATOR_URL}/api/metrics", params={"service": service}, timeout=5.0)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Failed to fetch metrics: {str(e)}"}
