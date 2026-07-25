from pydantic import BaseModel
from typing import Optional, List

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
