from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(50), unique=True, index=True, nullable=False) # e.g. INC-2026-001
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    incident_type = Column(String(50), default="operationnel") # securite, fraude, ecart_caisse, panne_technique, non_conformite
    severity = Column(String(50), default="significatif") # mineur, significatif, majeur, critique
    occurred_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    detected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String(50), default="declare") # declare, qualifie, en_traitement, resolu, clos
    
    reporter_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assigned_to_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    impact_summary = Column(Text, nullable=True)
    resolution_summary = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    root_cause = Column(Text, nullable=True)
    lessons_learned = Column(Text, nullable=True) # INC-04 : REX obligatoire pour clôture
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    reporter = relationship("User", foreign_keys=[reporter_id])
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
