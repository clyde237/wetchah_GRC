from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Questionnaire(Base):
    __tablename__ = "questionnaires"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    target_type = Column(String(50), default="interne") # interne, tiers, controle_decentralise
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    questions = relationship("Question", back_populates="questionnaire", cascade="all, delete-orphan")
    campaigns = relationship("EvaluationCampaign", back_populates="questionnaire", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    questionnaire_id = Column(Integer, ForeignKey("questionnaires.id", ondelete="CASCADE"), nullable=False)
    order_num = Column(Integer, default=1)
    section = Column(String(100), default="Général")
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), default="yes_no") # yes_no, scale_1_5, text, choice
    is_risk_trigger = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    questionnaire = relationship("Questionnaire", back_populates="questions")

class EvaluationCampaign(Base):
    __tablename__ = "evaluation_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    questionnaire_id = Column(Integer, ForeignKey("questionnaires.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    deadline = Column(DateTime, nullable=False)
    status = Column(String(50), default="en_cours") # brouillon, en_cours, terminee
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    questionnaire = relationship("Questionnaire", back_populates="campaigns")
    responses = relationship("CampaignResponse", back_populates="campaign", cascade="all, delete-orphan")

class CampaignResponse(Base):
    __tablename__ = "campaign_responses"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("evaluation_campaigns.id", ondelete="CASCADE"), nullable=False)
    respondent_name = Column(String(255), nullable=False)
    respondent_email = Column(String(255), nullable=False)
    access_token = Column(String(100), unique=True, index=True, nullable=False)
    is_completed = Column(Boolean, default=False)
    score = Column(Float, default=0.0)
    completed_at = Column(DateTime, nullable=True)
    answers_json = Column(Text, nullable=True) # JSON sérialisé des réponses
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    campaign = relationship("EvaluationCampaign", back_populates="responses")
