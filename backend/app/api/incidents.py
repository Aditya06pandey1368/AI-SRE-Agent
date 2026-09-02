from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Incident, Alert, InvestigationStep, RemediationAction, Postmortem
from app.schemas import Incident as IncidentSchema, Alert as AlertSchema, RemediationAction as RemediationActionSchema, Postmortem as PostmortemSchema

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

# Additional endpoints will be added later for investigate, approve, reject, remediate
