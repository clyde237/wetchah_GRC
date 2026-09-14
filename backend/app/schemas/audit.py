from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class ControlBase(BaseModel):
    code: str
    title: str
    description: str
    control_type: str = "operationnel"
    frequency: str = "mensuel"
    method: str = "manuel"
    owner_id: Optional[int] = None
    status: str = "actif"

class ControlCreate(ControlBase):
    pass

class ControlOut(ControlBase):
    id: int
    last_test_date: Optional[datetime] = None
    last_test_result: Optional[str] = "conforme"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ControlTestCreate(BaseModel):
    control_id: int
    result: str # conforme, non_conforme, partiellement_conforme
    observations: Optional[str] = None
    evidence_file: Optional[str] = None

class ControlTestOut(BaseModel):
    id: int
    control_id: int
    tester_id: Optional[int]
    test_date: datetime
    result: str
    observations: Optional[str]
    evidence_file: Optional[str]

    class Config:
        from_attributes = True

class ActionPlanBase(BaseModel):
    finding_id: Optional[int] = None
    risk_id: Optional[int] = None
    title: str
    description: str
    assignee_id: Optional[int] = None
    due_date: datetime
    status: str = "non_debute"

class ActionPlanCreate(ActionPlanBase):
    pass

class ActionPlanUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None
    completion_date: Optional[datetime] = None

class ActionPlanOut(ActionPlanBase):
    id: int
    completion_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FindingBase(BaseModel):
    code: str
    title: str
    description: str
    severity: str = "moyen"
    control_id: Optional[int] = None
    recommendation: str

class FindingCreate(FindingBase):
    mission_id: int

class FindingOut(FindingBase):
    id: int
    mission_id: int
    created_at: datetime
    action_plans: Optional[List[ActionPlanOut]] = []

    class Config:
        from_attributes = True

class AuditMissionBase(BaseModel):
    reference: str
    title: str
    scope: str
    lead_auditor_id: Optional[int] = None
    start_date: datetime
    end_date: datetime
    status: str = "planifiee"
    summary_notes: Optional[str] = None

class AuditMissionCreate(AuditMissionBase):
    pass

class AuditMissionOut(AuditMissionBase):
    id: int
    created_at: datetime
    findings: Optional[List[FindingOut]] = []

    class Config:
        from_attributes = True
