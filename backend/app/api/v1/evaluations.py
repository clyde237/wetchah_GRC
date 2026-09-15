import json
import secrets
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_roles, record_activity
from app.models.evaluation import Questionnaire, Question, EvaluationCampaign, CampaignResponse
from app.models.user import User
from app.schemas.evaluation import (
    QuestionnaireCreate, QuestionnaireOut, CampaignCreate, CampaignOut,
    RespondentFormOut, RespondentQuestionOut, SubmitResponseIn, SubmitResponseOut,
    CampaignResponseOut, CampaignResponseDetailOut, AnsweredQuestionOut,
)
from app.services.evaluation_scoring import score_answer, is_triggered, campaign_score

router = APIRouter()


def _as_utc(value: Optional[datetime]) -> Optional[datetime]:
    """SQLite rend des datetime naïfs ; on les rattache à UTC pour comparer."""
    if value is None:
        return None
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def _payload(response: CampaignResponse) -> dict:
    """Contenu de answers_json, tolérant à l'absence ou à un JSON abîmé."""
    if not response.answers_json:
        return {}
    try:
        data = json.loads(response.answers_json)
        return data if isinstance(data, dict) else {}
    except ValueError:
        return {}

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
        out = CampaignOut.model_validate(c)
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
    out = CampaignOut.model_validate(c)
    out.total_responses = len(c_in.respondents)
    out.completed_responses = 0
    return out


@router.get("/campaigns/{campaign_id}/links")
def list_campaign_links(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "risk_manager", "auditor", "controller"]))
):
    """
    Liens d'accès individuels d'une campagne, à transmettre aux répondants.

    Aucun envoi automatique n'existe encore (pas de passerelle e-mail dans ce
    module) : le contrôleur récupère les liens ici et les diffuse par son
    propre canal. Réservé aux rôles habilités — un jeton est une clé d'accès.
    """
    campaign = db.query(EvaluationCampaign).filter(EvaluationCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campagne introuvable.")

    return [
        {
            "respondent_name": r.respondent_name,
            "respondent_email": r.respondent_email,
            "is_completed": r.is_completed,
            "path": f"/respond/{r.access_token}",
        }
        for r in campaign.responses
    ]


@router.get("/campaigns/{campaign_id}/responses", response_model=List[CampaignResponseOut])
def list_campaign_responses(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Dépouillement d'une campagne : qui a répondu, avec quel score."""
    campaign = db.query(EvaluationCampaign).filter(EvaluationCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campagne introuvable.")

    out = []
    for r in campaign.responses:
        data = _payload(r)
        item = CampaignResponseOut.model_validate(r)
        item.triggered_count = len(data.get("triggered", []))
        item.is_late = bool(data.get("late", False))
        out.append(item)
    return out


@router.get("/campaigns/{campaign_id}/responses/{response_id}", response_model=CampaignResponseDetailOut)
def get_campaign_response(
    campaign_id: int,
    response_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Détail d'une réponse : chaque question, la réponse donnée, sa note et le
    fait qu'elle ait déclenché un signalement. C'est la pièce que le
    contrôleur verse à son dossier d'audit.
    """
    response = db.query(CampaignResponse).filter(
        CampaignResponse.id == response_id,
        CampaignResponse.campaign_id == campaign_id,
    ).first()
    if not response:
        raise HTTPException(status_code=404, detail="Réponse introuvable pour cette campagne.")

    data = _payload(response)
    given = {int(a["question_id"]): a.get("value") for a in data.get("answers", []) if "question_id" in a}
    triggered = set(data.get("triggered", []))

    questions = db.query(Question).filter(
        Question.questionnaire_id == response.campaign.questionnaire_id
    ).order_by(Question.order_num).all()

    detail = CampaignResponseDetailOut.model_validate(response)
    detail.campaign_id = campaign_id
    detail.triggered_count = len(triggered)
    detail.is_late = bool(data.get("late", False))
    detail.answers = [
        AnsweredQuestionOut(
            question_id=q.id,
            question_text=q.question_text,
            section=q.section,
            question_type=q.question_type,
            value=given.get(q.id),
            scored_value=score_answer(q.question_type, given.get(q.id)),
            is_risk_trigger=q.is_risk_trigger,
            triggered=q.id in triggered,
        )
        for q in questions
    ]
    return detail


# ── Accès répondant : public, authentifié par le seul jeton de la campagne ──

@router.get("/respond/{token}", response_model=RespondentFormOut)
def get_respondent_form(token: str, db: Session = Depends(get_db)):
    """
    Formulaire vu par un répondant. Volontairement sans authentification :
    les répondants (chefs de service, fournisseurs) n'ont pas de compte GRC.
    Le jeton tiré au hasard à la création de la campagne fait office de clé,
    et n'ouvre l'accès qu'à ce seul formulaire.
    """
    response = db.query(CampaignResponse).filter(CampaignResponse.access_token == token).first()
    if not response:
        raise HTTPException(status_code=404, detail="Lien d'évaluation inconnu ou expiré.")

    campaign = response.campaign
    questions = db.query(Question).filter(
        Question.questionnaire_id == campaign.questionnaire_id
    ).order_by(Question.order_num).all()

    deadline = _as_utc(campaign.deadline)

    return RespondentFormOut(
        campaign_title=campaign.title,
        questionnaire_title=campaign.questionnaire.title,
        questionnaire_description=campaign.questionnaire.description,
        deadline=campaign.deadline,
        respondent_name=response.respondent_name,
        is_completed=response.is_completed,
        is_closed=campaign.status == "terminee",
        is_past_deadline=bool(deadline and datetime.now(timezone.utc) > deadline),
        questions=[RespondentQuestionOut.model_validate(q) for q in questions],
    )


@router.post("/respond/{token}", response_model=SubmitResponseOut)
def submit_respondent_form(token: str, payload: SubmitResponseIn, db: Session = Depends(get_db)):
    """
    Enregistre les réponses, calcule le score et relève les questions
    sensibles mal notées. Une réponse ne peut être soumise qu'une fois :
    autoriser la reprise reviendrait à laisser réécrire une déclaration déjà
    versée au dossier.

    Le détail est stocké dans answers_json (colonne existante) : aucune
    évolution de schéma n'est nécessaire, ce module n'ayant pas encore de
    mécanisme de migration.
    """
    response = db.query(CampaignResponse).filter(CampaignResponse.access_token == token).first()
    if not response:
        raise HTTPException(status_code=404, detail="Lien d'évaluation inconnu ou expiré.")

    if response.is_completed:
        raise HTTPException(status_code=409, detail="Cette évaluation a déjà été soumise.")

    campaign = response.campaign
    if campaign.status == "terminee":
        raise HTTPException(status_code=409, detail="Cette campagne est clôturée : les réponses ne sont plus acceptées.")

    questions = {
        q.id: q for q in db.query(Question).filter(
            Question.questionnaire_id == campaign.questionnaire_id
        ).all()
    }

    answers = []
    scored_values = []
    triggered = []

    for answer in payload.answers:
        question = questions.get(answer.question_id)
        if not question:
            # Une question étrangère au questionnaire est ignorée plutôt que
            # de faire échouer toute la soumission du répondant.
            continue

        value = (answer.value or "").strip()
        scored = score_answer(question.question_type, value)

        answers.append({"question_id": question.id, "value": value})
        if scored is not None:
            scored_values.append(scored)
        if is_triggered(question.is_risk_trigger, scored):
            triggered.append(question.id)

    if not answers:
        raise HTTPException(status_code=400, detail="Aucune réponse exploitable n'a été transmise.")

    now = datetime.now(timezone.utc)
    deadline = _as_utc(campaign.deadline)
    is_late = bool(deadline and now > deadline)

    response.answers_json = json.dumps({
        "answers": answers,
        "triggered": triggered,
        "submitted_at": now.isoformat(),
        "late": is_late,
    }, ensure_ascii=False)
    response.score = campaign_score(scored_values)
    response.is_completed = True
    response.completed_at = now
    db.commit()

    # Pas d'utilisateur GRC derrière cette action : le journal retient le
    # répondant, seule identité disponible.
    record_activity(
        db, None, "SUBMIT", "CAMPAIGN_RESPONSE", str(response.id),
        f"Réponse de {response.respondent_name} à « {campaign.title} » — "
        f"score {response.score}/100, {len(triggered)} point(s) d'attention"
    )

    return SubmitResponseOut(
        score=response.score,
        answered=len(answers),
        scored=len(scored_values),
        is_late=is_late,
        message="Merci, votre évaluation a bien été enregistrée.",
    )
