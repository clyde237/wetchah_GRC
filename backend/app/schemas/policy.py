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

    class Config:
        from_attributes = True
