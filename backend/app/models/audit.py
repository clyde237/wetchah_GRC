from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class InternalControl(Base):
    __tablename__ = "internal_controls"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False) # e.g. CTRL-CAISSE-01
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    control_type = Column(String(50), default="operationnel") # financier, operationnel, informatique
    frequency = Column(String(50), default="mensuel") # quotidien, hebdomadaire, mensuel, trimestriel, annuel
    method = Column(String(50), default="manuel") # manuel, semi_automatise, automatise
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(50), default="actif") # actif, en_revue, inactif
    last_test_date = Column(DateTime, nullable=True)
    last_test_result = Column(String(50), default="conforme") # conforme, non_conforme, partiellement_conforme
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    owner = relationship("User", foreign_keys=[owner_id])
    tests = relationship("ControlTest", back_populates="control", cascade="all, delete-orphan")

class ControlTest(Base):
    __tablename__ = "control_tests"

    id = Column(Integer, primary_key=True, index=True)
    control_id = Column(Integer, ForeignKey("internal_controls.id", ondelete="CASCADE"), nullable=False)
    tester_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    test_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    result = Column(String(50), nullable=False) # conforme, non_conforme, partiellement_conforme
    observations = Column(Text, nullable=True)
    evidence_file = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    control = relationship("InternalControl", back_populates="tests")
    tester = relationship("User", foreign_keys=[tester_id])

class AuditMission(Base):
    __tablename__ = "audit_missions"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(50), unique=True, index=True, nullable=False) # e.g. AUD-2026-Q3
    title = Column(String(255), nullable=False)
    scope = Column(Text, nullable=False)
    lead_auditor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String(50), default="planifiee") # planifiee, en_cours, en_revue, terminee
    summary_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    lead_auditor = relationship("User", foreign_keys=[lead_auditor_id])
    findings = relationship("AuditFinding", back_populates="mission", cascade="all, delete-orphan")

class AuditFinding(Base):
    __tablename__ = "audit_findings"

    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("audit_missions.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(50), nullable=False) # e.g. CONST-01
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(50), default="moyen") # faible, moyen, eleve, critique
    control_id = Column(Integer, ForeignKey("internal_controls.id", ondelete="SET NULL"), nullable=True)
    recommendation = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    mission = relationship("AuditMission", back_populates="findings")
    control = relationship("InternalControl", foreign_keys=[control_id])
    action_plans = relationship("ActionPlan", back_populates="finding", cascade="all, delete-orphan")

class ActionPlan(Base):
    __tablename__ = "action_plans"

    id = Column(Integer, primary_key=True, index=True)
    finding_id = Column(Integer, ForeignKey("audit_findings.id", ondelete="CASCADE"), nullable=True)
    risk_id = Column(Integer, ForeignKey("risks.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    due_date = Column(DateTime, nullable=False)
    status = Column(String(50), default="non_debute") # non_debute, en_cours, realise, en_retard, valide
    completion_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    finding = relationship("AuditFinding", back_populates="action_plans")
    assignee = relationship("User", foreign_keys=[assignee_id])
