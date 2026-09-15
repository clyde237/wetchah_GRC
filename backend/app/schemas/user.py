import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator

class UserBase(BaseModel):
    email: str
    full_name: str
    role: str = "controller"
    department: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v):
            raise ValueError("Adresse email invalide")
        return v

class UserCreate(UserBase):
    password: str

    # Renseignée par l'ERP quand l'adresse du compte a changé : sans elle, le
    # provisioning créerait un second compte et laisserait l'ancien ouvrir
    # encore le portail.
    previous_email: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None

class UserOut(UserBase):
    id: int
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ActivityLogOut(BaseModel):
    id: int
    user_id: Optional[int]
    user_name: Optional[str]
    action: str
    resource_type: str
    resource_id: Optional[str]
    details: Optional[str]
    ip_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
