import httpx
import os
from typing import List, Dict, Any

SIMULATOR_URL = os.getenv("SIMULATOR_URL", "http://localhost:8001")

def get_recent_deployments(service: str) -> List[Dict[str, Any]]:
    """
    Fetches the recent deployments for a given service.
    Returns a list of deployments with service, version, and timestamp.
    """
    try:
        response = httpx.get(f"{SIMULATOR_URL}/api/deployments", params={"service": service}, timeout=5.0)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return [{"error": f"Failed to fetch deployments: {str(e)}"}]
