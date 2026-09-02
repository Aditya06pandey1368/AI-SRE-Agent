from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Any, Dict

from app.database import get_db
from app.models import Alert, Incident, Service, Postmortem
from app.schemas import WebhookPayload
import uuid

from app.graph.workflow import create_incident_workflow
import json

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])

def trigger_investigation(incident_id: str, db: Session):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        return

    # In a real app we'd fetch the latest alert for this incident
    alert = db.query(Alert).filter(Alert.incident_id == incident_id).order_by(Alert.timestamp.desc()).first()
    
    workflow = create_incident_workflow()
    
    initial_state = {
        "incident_id": incident_id,
        "service": incident.service_id,
        "alert": alert.payload if alert else {},
        "severity": incident.severity,
        "metrics": {},
        "logs": [],
        "deployments": [],
        "investigation_history": [],
        "iteration_count": 0,
        "approval_status": "not_required"
    }
    
    final_state = workflow.invoke(initial_state)
    
    # Update DB with final state
    incident.root_cause = final_state.get("root_cause")
    incident.confidence = final_state.get("confidence")
    incident.status = "pending_approval" if final_state.get("approval_status") == "pending" else "investigating"
    
    if final_state.get("final_report"):
        pm = Postmortem(incident_id=incident_id, content=final_state["final_report"])
        db.add(pm)
        incident.status = "resolved"
        
    db.commit()

@router.post("/webhook")
def receive_alert(payload: WebhookPayload, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Receives an alert from an external monitoring system (or our simulator).
    Creates an incident if needed and triggers the agentic investigation.
    """
    
    # 1. Ensure service exists (auto-create for demo purposes)
    service = db.query(Service).filter(Service.id == payload.service).first()
    if not service:
        service = Service(id=payload.service, name=payload.service, description="Auto-registered service")
        db.add(service)
        db.commit()

    # 2. Check for active incident for this service
    incident = db.query(Incident).filter(
        Incident.service_id == payload.service,
        Incident.status.in_(["active", "investigating", "pending_approval"])
    ).first()
    
    is_new = False
    if not incident:
        is_new = True
        incident_id = f"INC-{str(uuid.uuid4())[:8].upper()}"
        incident = Incident(
            id=incident_id,
            title=f"[{payload.severity.upper()}] {payload.alert_name} on {payload.service}",
            service_id=payload.service,
            severity=payload.severity,
            status="active"
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)

    # 3. Record the alert
    alert = Alert(
        incident_id=incident.id,
        source=payload.source,
        alert_name=payload.alert_name,
        severity=payload.severity,
        payload=payload.model_dump()
    )
    db.add(alert)
    db.commit()
    
    # 4. Trigger LangGraph Agent Workflow
    if is_new:
        # We run it in the background to not block the webhook response
        background_tasks.add_task(trigger_investigation, incident.id, db)
        
    return {"status": "success", "message": "Alert received", "incident_id": incident.id}
