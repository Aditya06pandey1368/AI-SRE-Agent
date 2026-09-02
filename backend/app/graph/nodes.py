import os
from typing import Dict, Any, List
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate

from app.graph.state import IncidentState
from app.tools.metrics import get_service_metrics
from app.tools.logs import search_service_logs
from app.tools.deployments import get_recent_deployments

class RootCauseAnalysis(BaseModel):
    root_cause: str = Field(description="The probable root cause of the incident")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    reasoning_summary: str = Field(description="Brief summary of the reasoning based on evidence")
    recommended_action: str = Field(description="Recommended action to remediate (e.g., 'rollback', 'restart', 'scale', 'none')")

class RemediationPlan(BaseModel):
    action: str
    service: str
    version: str = None
    replicas: int = None

def get_llm():
    # Use Llama 3 for structured output and fast reasoning via Groq
    return ChatGroq(model_name="llama3-70b-8192", temperature=0)

def collect_evidence_node(state: IncidentState) -> Dict[str, Any]:
    service = state["service"]
    metrics = get_service_metrics(service)
    logs = search_service_logs(service, limit=20)
    deployments = get_recent_deployments(service)
    
    return {
        "metrics": metrics,
        "logs": logs,
        "deployments": deployments,
        "iteration_count": state.get("iteration_count", 0) + 1,
        "investigation_history": state.get("investigation_history", []) + ["Collected metrics, logs, deployments."]
    }

def root_cause_analysis_node(state: IncidentState) -> Dict[str, Any]:
    llm = get_llm()
    structured_llm = llm.with_structured_output(RootCauseAnalysis)
    
    prompt = PromptTemplate.from_template(
        """You are an expert Site Reliability Engineer investigating an incident.
        Analyze the following curated evidence and determine the root cause.
        
        Incident on Service: {service}
        Alert: {alert}
        
        Metrics:
        {metrics}
        
        Recent Logs:
        {logs}
        
        Recent Deployments:
        {deployments}
        
        Provide your analysis carefully. Do not hallucinate evidence. 
        If confidence is low, recommend "investigate_more".
        """
    )
    
    chain = prompt | structured_llm
    
    response: RootCauseAnalysis = chain.invoke({
        "service": state["service"],
        "alert": state["alert"],
        "metrics": state["metrics"],
        "logs": state["logs"],
        "deployments": state["deployments"]
    })
    
    action_dict = {"action": response.recommended_action, "service": state["service"]}
    if response.recommended_action == "rollback" and state["deployments"]:
        action_dict["version"] = state["deployments"][0].get("version")
        
    return {
        "root_cause": response.root_cause,
        "confidence": response.confidence,
        "reasoning_summary": response.reasoning_summary,
        "recommended_action": action_dict,
        "investigation_history": state.get("investigation_history", []) + [f"Analyzed root cause: {response.root_cause} (Confidence: {response.confidence})"]
    }

def safety_policy_node(state: IncidentState) -> Dict[str, Any]:
    # Deterministic policy engine
    allowed_actions = ["restart", "rollback", "scale"]
    action = state["recommended_action"]["action"]
    
    if action not in allowed_actions:
        return {"approval_status": "rejected", "investigation_history": state.get("investigation_history", []) + ["Action rejected by policy engine."]}
        
    if state["confidence"] < 0.7:
        return {"approval_status": "rejected", "investigation_history": state.get("investigation_history", []) + ["Action rejected due to low confidence."]}
        
    return {"approval_status": "pending", "investigation_history": state.get("investigation_history", []) + ["Action requires human approval."]}

def human_approval_node(state: IncidentState) -> Dict[str, Any]:
    # In a real app, we pause the graph here using LangGraph's memory/interrupt
    # For now, we simulate approval or wait for external signal.
    # We will implement actual interrupt in the workflow definition.
    return {}

def execute_remediation_node(state: IncidentState) -> Dict[str, Any]:
    import httpx
    # Call simulator API
    SIMULATOR_URL = os.getenv("SIMULATOR_URL", "http://localhost:8001")
    try:
        res = httpx.post(f"{SIMULATOR_URL}/api/remediate", json=state["recommended_action"])
        result = res.json()
    except Exception as e:
        result = {"status": "failed", "error": str(e)}
        
    return {
        "execution_result": result,
        "investigation_history": state.get("investigation_history", []) + [f"Executed remediation: {result.get('status')}"]
    }

def verify_recovery_node(state: IncidentState) -> Dict[str, Any]:
    metrics = get_service_metrics(state["service"])
    
    # Deterministic check
    recovered = False
    if metrics.get("error_rate", 100) < 5.0 and metrics.get("latency_p95", 1000) < 500:
        recovered = True
        
    return {
        "verification_result": {"recovered": recovered, "metrics_snapshot": metrics},
        "investigation_history": state.get("investigation_history", []) + [f"Verified recovery: {recovered}"]
    }

def generate_postmortem_node(state: IncidentState) -> Dict[str, Any]:
    llm = get_llm()
    prompt = PromptTemplate.from_template(
        """Write a concise incident postmortem.
        
        Service: {service}
        Root Cause: {root_cause}
        Action Taken: {action}
        Recovery Status: {recovery}
        Reasoning: {reasoning}
        
        Include sections:
        - Incident Summary
        - Root Cause
        - Remediation
        - Lessons Learned
        """
    )
    
    response = llm.invoke(prompt.format(
        service=state["service"],
        root_cause=state["root_cause"],
        action=state["recommended_action"],
        recovery=state.get("verification_result", {}).get("recovered"),
        reasoning=state["reasoning_summary"]
    ))
    
    return {"final_report": response.content}
