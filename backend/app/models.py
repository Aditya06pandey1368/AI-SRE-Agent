from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

class Service(Base):
    __tablename__ = "services"
    id = Column(String, primary_key=True, index=True) # e.g. "payment-api"
    name = Column(String)
    description = Column(String)

class Incident(Base):
    __tablename__ = "incidents"
    id = Column(String, primary_key=True, index=True) # e.g. "INC-1024"
    title = Column(String)
    service_id = Column(String, ForeignKey("services.id"))
    severity = Column(String) # critical, warning
    status = Column(String, default="active") # active, investigating, pending_approval, resolved
    root_cause = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    service = relationship("Service")

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String, ForeignKey("incidents.id"))
    source = Column(String)
    alert_name = Column(String)
    severity = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    payload = Column(JSON) # original alert payload

class InvestigationStep(Base):
    __tablename__ = "investigation_steps"
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String, ForeignKey("incidents.id"))
    step_type = Column(String) # metrics, logs, deployment, root_cause
    tool_used = Column(String)
    llm_used = Column(Boolean, default=False)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    result = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RemediationAction(Base):
    __tablename__ = "remediation_actions"
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String, ForeignKey("incidents.id"))
    action_type = Column(String)
    target_service = Column(String)
    payload = Column(JSON)
    status = Column(String) # pending_approval, approved, rejected, executed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Postmortem(Base):
    __tablename__ = "postmortems"
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String, ForeignKey("incidents.id"))
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
