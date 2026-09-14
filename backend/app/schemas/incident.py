from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class IncidentBase(BaseModel):
    reference: str
    title: str
    description: str
    incident_type: str = "operationnel"
    severity: str = "significatif"
    occurred_at: datetime
    detected_at: datetime
    status: str = "declare"
    assigned_to_id: Optional[int] = None
    impact_summary: Optional[str] = None
    resolution_summary: Optional[str] = None
    root_cause: Optional[str] = None
    lessons_learned: Optional[str] = None

class IncidentCreate(IncidentBase):
    pass

class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    incident_type: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    assigned_to_id: Optional[int] = None
    impact_summary: Optional[str] = None
    resolution_summary: Optional[str] = None
    resolved_at: Optional[datetime] = None
    root_cause: Optional[str] = None
    lessons_learned: Optional[str] = None

class IncidentOut(IncidentBase):
    id: int
    reporter_id: Optional[int]
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
