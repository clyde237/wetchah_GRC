import secrets
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_roles, record_activity
from app.models.evaluation import Questionnaire, Question, EvaluationCampaign, CampaignResponse
from app.models.user import User
from app.schemas.evaluation import QuestionnaireCreate, QuestionnaireOut, CampaignCreate, CampaignOut

router = APIRouter()

@router.get("/questionnaires", response_model=List[QuestionnaireOut])
def list_questionnaires(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Questionnaire).all()

@router.post("/questionnaires", response_model=QuestionnaireOut, status_code=status.HTTP_201_CREATED)
def create_questionnaire(
    q_in: QuestionnaireCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "risk_manager", "auditor", "controller"]))
):
    q = Questionnaire(title=q_in.title, description=q_in.description, target_type=q_in.target_type)
    db.add(q)
    db.flush()

    for idx, question in enumerate(q_in.questions or [], 1):
        db.add(Question(
            questionnaire_id=q.id,
            order_num=idx,
            section=question.section,
            question_text=question.question_text,
            question_type=question.question_type,
            is_risk_trigger=question.is_risk_trigger
        ))
    db.commit()
    db.refresh(q)
    record_activity(db, current_user, "CREATE", "QUESTIONNAIRE", str(q.id), f"Questionnaire {q.title}")
    return q

@router.get("/campaigns", response_model=List[CampaignOut])
def list_campaigns(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    camps = db.query(EvaluationCampaign).all()
    results = []
    for c in camps:
        out = CampaignOut.from_orm(c)
        out.total_responses = len(c.responses)
        out.completed_responses = sum(1 for r in c.responses if r.is_completed)
        results.append(out)
    return results

@router.post("/campaigns", response_model=CampaignOut, status_code=status.HTTP_201_CREATED)
def launch_campaign(
    c_in: CampaignCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "risk_manager", "auditor", "controller"]))
):
    c = EvaluationCampaign(
        questionnaire_id=c_in.questionnaire_id,
        title=c_in.title,
        deadline=c_in.deadline,
        status="en_cours"
    )
    db.add(c)
    db.flush()

    for resp in c_in.respondents:
        token = secrets.token_urlsafe(24)
        db.add(CampaignResponse(
            campaign_id=c.id,
            respondent_name=resp.get("name", "Anonyme"),
            respondent_email=resp.get("email", ""),
            access_token=token
        ))
    db.commit()
    db.refresh(c)
    record_activity(db, current_user, "CREATE", "CAMPAIGN", str(c.id), f"Lancement campagne {c.title}")
    out = CampaignOut.from_orm(c)
    out.total_responses = len(c_in.respondents)
    out.completed_responses = 0
    return out
