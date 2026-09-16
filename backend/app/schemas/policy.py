from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class PolicyBase(BaseModel):
    code: str
    title: str
    document_type: str = "politique"
    current_version: str = "1.0"
    owner_id: Optional[int] = None
    status: str = "brouillon"
    review_frequency_days: int = 365
    next_review_date: Optional[datetime] = None
    content: Optional[str] = None
    file_url: Optional[str] = None

class PolicyCreate(PolicyBase):
    pass

class PolicyUpdate(BaseModel):
    title: Optional[str] = None
    document_type: Optional[str] = None
    current_version: Optional[str] = None
    owner_id: Optional[int] = None
    status: Optional[str] = None
    review_frequency_days: Optional[int] = None
    next_review_date: Optional[datetime] = None
    content: Optional[str] = None
    file_url: Optional[str] = None

class PolicyOut(PolicyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    version_count: int = 0
    acknowledgment_count: int = 0

    class Config:
        from_attributes = True


class PolicyVersionCreate(BaseModel):
    version_number: str
    change_summary: str
    approve: bool = False  # marque la version comme approuvée par l'auteur de l'appel


class PolicyVersionOut(BaseModel):
    id: int
    policy_id: int
    version_number: str
    change_summary: str
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PolicyAcknowledgmentOut(BaseModel):
    id: int
    user_id: int
    user_name: Optional[str] = None
    acknowledged_at: datetime

    class Config:
        from_attributes = True


class PolicyDetailOut(PolicyOut):
    versions: List[PolicyVersionOut] = []
    acknowledged_by_me: bool = False
    allowed_transitions: List[str] = []
