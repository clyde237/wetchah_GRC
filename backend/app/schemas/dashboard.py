from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class TopRiskItem(BaseModel):
    id: int
    code: str
    title: str
    category: str
    gross_score: int
    residual_score: int
    status: str

class DashboardMetrics(BaseModel):
    total_risks: int
    critical_risks: int
    overall_compliance_rate: float
    active_controls: int
    failed_controls: int
    open_audit_findings: int
    open_incidents: int
    active_action_plans: int
    delayed_action_plans: int
    top_risks: List[TopRiskItem]
    risks_by_category: Dict[str, int]
    heatmap: List[Dict[str, Any]]
    wetchah_financial_summary: Optional[Dict[str, Any]] = None
