from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class ServiceBase(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

class ServiceCreate(ServiceBase):
    pass

class Service(ServiceBase):
    model_config = ConfigDict(from_attributes=True)

class IncidentBase(BaseModel):
    id: str
    title: str
    service_id: str
    severity: str
    status: str = "active"

class IncidentCreate(IncidentBase):
    pass

class Incident(IncidentBase):
    root_cause: Optional[str] = None
    confidence: Optional[float] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    service: Optional[Service] = None

    model_config = ConfigDict(from_attributes=True)

class AlertBase(BaseModel):
    source: str
    alert_name: str
    severity: str
    payload: Dict[str, Any]

class AlertCreate(AlertBase):
    incident_id: str

class Alert(AlertBase):
    id: int
    incident_id: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

class WebhookPayload(BaseModel):
    source: str
    service: str
    severity: str
    alert_name: str
    timestamp: str
    labels: Dict[str, str] = {}
    annotations: Dict[str, str] = {}
    metrics: Dict[str, Any] = {}

class RemediationActionBase(BaseModel):
    action_type: str
    target_service: str
    payload: Dict[str, Any]
    status: str = "pending_approval"

class RemediationActionCreate(RemediationActionBase):
    incident_id: str

class RemediationAction(RemediationActionBase):
    id: int
    incident_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PostmortemBase(BaseModel):
    incident_id: str
    content: str

class Postmortem(PostmortemBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
