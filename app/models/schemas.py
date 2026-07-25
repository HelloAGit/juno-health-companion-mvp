from pydantic import BaseModel, Field
from typing import Literal, Optional

class PatientIntake(BaseModel):
    patient_id: str
    raw_transcript: str

class StructuredCaseSummary(BaseModel):
    primary_symptom: str
    duration: str
    severity: int
    additional_notes: Optional[str] = None

class CarePathRoute(BaseModel):
    route_id: str
    recommended_action: str
    urgency_level: str

class FollowUpMessage(BaseModel):
    patient_id: str
    message: str
    channel: str # 'voice' or 'chat'


class RecoveryCheckIn(BaseModel):
    """A deliberately small, structured post-discharge check-in."""

    patient_id: str
    recovery_day: int = Field(ge=1, le=30)
    symptom_change: Literal["better", "same", "worse"]
    pain_score: int = Field(ge=0, le=10)
    temperature_c: Optional[float] = Field(default=None, ge=30, le=45)
    medication_status: Literal["all", "some", "none", "not_sure"]
    notes: str = Field(default="", max_length=2000)
