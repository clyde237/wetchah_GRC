from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ThirdPartyBase(BaseModel):
    name: str
    category: str = "fournisseur"
    criticality: str = "moyen"
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    contract_reference: Optional[str] = None
    contract_expiry: Optional[datetime] = None
    risk_score: float = 0.0
    status: str = "actif"
    notes: Optional[str] = None

class ThirdPartyCreate(ThirdPartyBase):
    pass

class ThirdPartyUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    criticality: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    contract_reference: Optional[str] = None
    contract_expiry: Optional[datetime] = None
    risk_score: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class ThirdPartyOut(ThirdPartyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
