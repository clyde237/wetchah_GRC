from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class RequirementBase(BaseModel):
    clause_number: str
    title: str
    description: str
    compliance_status: str = "partiellement_conforme"
    gap_description: Optional[str] = None
    remediation_plan: Optional[str] = None
    target_date: Optional[datetime] = None
    responsible_id: Optional[int] = None
    evidence_notes: Optional[str] = None

class RequirementCreate(RequirementBase):
    framework_id: int

class RequirementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    compliance_status: Optional[str] = None
    gap_description: Optional[str] = None
    remediation_plan: Optional[str] = None
    target_date: Optional[datetime] = None
    responsible_id: Optional[int] = None
    evidence_notes: Optional[str] = None

class RequirementOut(RequirementBase):
    id: int
    framework_id: int
    updated_at: datetime

    class Config:
        from_attributes = True

class FrameworkBase(BaseModel):
    code: str
    name: str
    version: str = "2022"
    category: str = "Sécurité & Organisation"
    description: Optional[str] = None

class FrameworkCreate(FrameworkBase):
    pass

class FrameworkOut(FrameworkBase):
    id: int
    created_at: datetime
    compliance_rate: Optional[float] = 0.0
    requirements: Optional[List[RequirementOut]] = []

    class Config:
        from_attributes = True
