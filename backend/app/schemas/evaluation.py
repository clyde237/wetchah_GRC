from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class QuestionBase(BaseModel):
    order_num: int = 1
    section: str = "Général"
    question_text: str
    question_type: str = "yes_no"
    is_risk_trigger: bool = False

class QuestionCreate(QuestionBase):
    pass

class QuestionOut(QuestionBase):
    id: int
    questionnaire_id: int

    class Config:
        from_attributes = True

class QuestionnaireBase(BaseModel):
    title: str
    description: Optional[str] = None
    target_type: str = "interne"
    is_active: bool = True

class QuestionnaireCreate(QuestionnaireBase):
    questions: Optional[List[QuestionCreate]] = []

class QuestionnaireOut(QuestionnaireBase):
    id: int
    created_at: datetime
    questions: Optional[List[QuestionOut]] = []

    class Config:
        from_attributes = True

class CampaignCreate(BaseModel):
    questionnaire_id: int
    title: str
    deadline: datetime
    respondents: List[dict] # list of {"name": str, "email": str}

class CampaignOut(BaseModel):
    id: int
    questionnaire_id: int
    title: str
    deadline: datetime
    status: str
    created_at: datetime
    total_responses: Optional[int] = 0
    completed_responses: Optional[int] = 0

    class Config:
        from_attributes = True
