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


# ── Côté répondant (accès public par jeton, sans compte GRC) ────────────────

class RespondentQuestionOut(BaseModel):
    """Une question telle que la voit le répondant.

    `is_risk_trigger` est volontairement absent : le répondant n'a pas à
    savoir quelles réponses déclencheront un signalement, sans quoi il est
    tenté d'orienter ses réponses.
    """
    id: int
    order_num: int
    section: str
    question_text: str
    question_type: str

    class Config:
        from_attributes = True


class RespondentFormOut(BaseModel):
    campaign_title: str
    questionnaire_title: str
    questionnaire_description: Optional[str] = None
    deadline: datetime
    respondent_name: str
    is_completed: bool
    is_closed: bool           # campagne clôturée : plus aucune réponse acceptée
    is_past_deadline: bool    # échéance dépassée : réponse acceptée mais signalée
    questions: List[RespondentQuestionOut] = []


class AnswerIn(BaseModel):
    question_id: int
    value: str


class SubmitResponseIn(BaseModel):
    answers: List[AnswerIn]


class SubmitResponseOut(BaseModel):
    score: float
    answered: int
    scored: int
    is_late: bool
    message: str


# ── Côté contrôleur : dépouillement d'une campagne ──────────────────────────

class CampaignResponseOut(BaseModel):
    id: int
    respondent_name: str
    respondent_email: str
    is_completed: bool
    score: float
    completed_at: Optional[datetime] = None
    triggered_count: int = 0
    is_late: bool = False

    class Config:
        from_attributes = True


class AnsweredQuestionOut(BaseModel):
    question_id: int
    question_text: str
    section: str
    question_type: str
    value: Optional[str] = None
    scored_value: Optional[float] = None
    is_risk_trigger: bool = False
    triggered: bool = False


class CampaignResponseDetailOut(CampaignResponseOut):
    campaign_id: int
    answers: List[AnsweredQuestionOut] = []
