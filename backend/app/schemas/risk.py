from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class RiskBase(BaseModel):
    code: str
    title: str
    description: str
    category: str = "operationnel"
    process_affected: Optional[str] = None
    asset_affected: Optional[str] = None
    third_party_id: Optional[int] = None
    owner_id: Optional[int] = None
    status: str = "identifie"
    gross_impact: int = 3
    gross_likelihood: int = 3
    residual_impact: int = 2
    residual_likelihood: int = 2
    treatment_strategy: str = "reduire"
    treatment_plan: Optional[str] = None
    review_frequency_days: int = 90
    next_review_date: Optional[datetime] = None

class RiskCreate(RiskBase):
    pass

class RiskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    process_affected: Optional[str] = None
    asset_affected: Optional[str] = None
    third_party_id: Optional[int] = None
    owner_id: Optional[int] = None
    status: Optional[str] = None
    gross_impact: Optional[int] = None
    gross_likelihood: Optional[int] = None
    residual_impact: Optional[int] = None
    residual_likelihood: Optional[int] = None
    treatment_strategy: Optional[str] = None
    treatment_plan: Optional[str] = None
    review_frequency_days: Optional[int] = None
    next_review_date: Optional[datetime] = None

class RiskOut(RiskBase):
    id: int
    gross_score: int
    residual_score: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class HeatmapCell(BaseModel):
    impact: int
    likelihood: int
    count: int
    risk_ids: List[int]
