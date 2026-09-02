from typing import TypedDict, List, Dict, Any, Optional
import operator

class IncidentState(TypedDict):
    incident_id: str
    alert: Dict[str, Any]
    severity: str
    service: str
    
    # Evidence collected deterministically
    metrics: Dict[str, Any]
    logs: List[Dict[str, Any]]
    deployments: List[Dict[str, Any]]
    
    investigation_history: List[str]
    
    # LLM reasoning outputs
    root_cause: Optional[str]
    confidence: float
    reasoning_summary: Optional[str]
    recommended_action: Optional[Dict[str, Any]]
    
    # Execution & Workflow tracking
    approval_status: str # "pending", "approved", "rejected", "not_required"
    execution_result: Optional[Dict[str, Any]]
    verification_result: Optional[Dict[str, Any]]
    final_report: Optional[str]
    iteration_count: int
