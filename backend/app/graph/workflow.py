from langgraph.graph import StateGraph, END
from app.graph.state import IncidentState
from app.graph.nodes import (
    collect_evidence_node,
    root_cause_analysis_node,
    safety_policy_node,
    human_approval_node,
    execute_remediation_node,
    verify_recovery_node,
    generate_postmortem_node
)

def create_incident_workflow():
    workflow = StateGraph(IncidentState)

    # Add nodes
    workflow.add_node("collect_evidence", collect_evidence_node)
    workflow.add_node("analyze_root_cause", root_cause_analysis_node)
    workflow.add_node("policy_check", safety_policy_node)
    workflow.add_node("human_approval", human_approval_node)
    workflow.add_node("execute_remediation", execute_remediation_node)
    workflow.add_node("verify_recovery", verify_recovery_node)
    workflow.add_node("generate_postmortem", generate_postmortem_node)

    # Define edges
    workflow.set_entry_point("collect_evidence")
    workflow.add_edge("collect_evidence", "analyze_root_cause")
    
    # Conditional logic for routing based on confidence
    def should_remediate(state: IncidentState):
        if state["confidence"] < 0.7:
            if state.get("iteration_count", 0) < 3:
                return "collect_more_evidence"
            return "end" # Give up after 3 tries
        return "policy_check"

    workflow.add_conditional_edges(
        "analyze_root_cause",
        should_remediate,
        {
            "collect_more_evidence": "collect_evidence",
            "policy_check": "policy_check",
            "end": END
        }
    )

    def route_policy(state: IncidentState):
        if state.get("approval_status") == "pending":
            return "human_approval"
        return "end"

    workflow.add_conditional_edges(
        "policy_check",
        route_policy,
        {
            "human_approval": "human_approval",
            "end": END
        }
    )

    # After human approval, if approved, execute, else end
    def route_approval(state: IncidentState):
        if state.get("approval_status") == "approved":
            return "execute_remediation"
        return "end"

    workflow.add_conditional_edges(
        "human_approval",
        route_approval,
        {
            "execute_remediation": "execute_remediation",
            "end": END
        }
    )

    workflow.add_edge("execute_remediation", "verify_recovery")

    def route_verification(state: IncidentState):
        if state.get("verification_result", {}).get("recovered"):
            return "generate_postmortem"
        return "end"

    workflow.add_conditional_edges(
        "verify_recovery",
        route_verification,
        {
            "generate_postmortem": "generate_postmortem",
            "end": END
        }
    )

    workflow.add_edge("generate_postmortem", END)

    # We can compile with a memory saver later to enable interrupts
    return workflow.compile()
