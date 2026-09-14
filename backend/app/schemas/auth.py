from typing import Optional
import re
from pydantic import BaseModel, field_validator
from app.schemas.user import UserOut

class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v):
            raise ValueError("Adresse email invalide")
        return v

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None

from app.schemas.user import UserOut
Token.model_rebuild()
