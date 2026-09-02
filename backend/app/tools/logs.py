import httpx
import os
from typing import List, Dict, Any

SIMULATOR_URL = os.getenv("SIMULATOR_URL", "http://localhost:8001")

def search_service_logs(service: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Searches recent logs for a given service.
    Returns a list of log entries with timestamp, severity, and message.
    """
    try:
        response = httpx.get(f"{SIMULATOR_URL}/api/logs", params={"service": service, "limit": limit}, timeout=5.0)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return [{"error": f"Failed to fetch logs: {str(e)}"}]
