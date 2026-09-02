from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Incident, Alert, Postmortem
from app.schemas import Incident as IncidentSchema, Alert as AlertSchema

from app.graph.workflow import create_incident_workflow

router = APIRouter(prefix="/api/v1/incidents", tags=["incidents"])

@router.get("", response_model=List[IncidentSchema])
def get_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).order_by(Incident.created_at.desc()).all()

@router.get("/{incident_id}", response_model=IncidentSchema)
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.get("/{incident_id}/alerts", response_model=List[AlertSchema])
def get_incident_alerts(incident_id: str, db: Session = Depends(get_db)):
    return db.query(Alert).filter(Alert.incident_id == incident_id).order_by(Alert.timestamp.desc()).all()

def execute_post_approval(incident_id: str, db: Session):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident or incident.status != "approved":
        return
        
    workflow = create_incident_workflow()
    
    # We resume execution from execute_remediation manually 
    # For a production system we'd use LangGraph persistent checkpointers
    state = {
        "incident_id": incident_id,
        "service": incident.service_id,
        "alert": {},
        "severity": incident.severity,
        "metrics": {},
        "logs": [],
        "deployments": [],
        "investigation_history": ["Human approved remediation."],
        "iteration_count": 1,
        "approval_status": "approved",
        "root_cause": incident.root_cause,
        "confidence": incident.confidence,
        # Reconstruct action (simplified for demo)
        "recommended_action": {"action": "rollback", "service": incident.service_id, "version": "v1.41"}
    }
    
    # Run the remaining nodes manually or via graph
    # For simplicity, we just call the nodes
    from app.graph.nodes import execute_remediation_node, verify_recovery_node, generate_postmortem_node
    
    res1 = execute_remediation_node(state)
    state.update(res1)
    
    res2 = verify_recovery_node(state)
    state.update(res2)
    
    if state.get("verification_result", {}).get("recovered"):
        res3 = generate_postmortem_node(state)
        state.update(res3)
        pm = Postmortem(incident_id=incident_id, content=state["final_report"])
        db.add(pm)
        incident.status = "resolved"
    else:
        incident.status = "investigating" # Failed to recover
        
    db.commit()


@router.post("/{incident_id}/approve")
def approve_incident(incident_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    incident.status = "approved"
    db.commit()
    
    background_tasks.add_task(execute_post_approval, incident_id, db)
    return {"status": "success", "message": "Incident approved and remediation started"}

@router.post("/{incident_id}/reject")
def reject_incident(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    incident.status = "investigating"
    db.commit()
    return {"status": "success", "message": "Incident rejected"}
