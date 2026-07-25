from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.models.schemas import PatientIntake, RecoveryCheckIn
from app.services.elevenlabs_service import (
    TranscriptionConfigurationError,
    TranscriptionRequestError,
    transcribe_audio,
)
from app.services.openai_service import generate_structured_summary
from app.services.juno_service import route_to_care_path
from app.services.follow_up_service import trigger_follow_up

app = FastAPI(
    title="Relay72 MVP",
    description="A focused 72-hour post-discharge safety-net prototype.",
)

WEB_APP = Path(__file__).resolve().parent.parent / "web" / "index.html"


@app.get("/", include_in_schema=False)
async def web_app():
    return FileResponse(WEB_APP)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "product": "Relay72"}


@app.post("/api/v1/transcribe", summary="Transcribe a short voice check-in")
async def transcribe_check_in(audio: UploadFile = File(...)):
    try:
        transcript = await transcribe_audio(
            audio=await audio.read(),
            filename=audio.filename or "relay72-check-in.webm",
            content_type=audio.content_type or "application/octet-stream",
        )
        return {"status": "success", "transcript": transcript}
    except TranscriptionConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except TranscriptionRequestError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/v1/intake", summary="Process Voice Intake and Route")
async def process_intake(intake: PatientIntake):
    try:
        # Step 1: LLM creates structured summary from voice transcript
        case_summary = generate_structured_summary(intake.raw_transcript)
        
        # Step 2: Juno routes the case based on structured data
        care_path = route_to_care_path(case_summary)
        
        # Step 3: Trigger the continuous companion follow-up loop
        # (In a real app, you might schedule this for 24 hours later)
        follow_up = trigger_follow_up(intake.patient_id, care_path.recommended_action)
        
        return {
            "status": "success",
            "patient_id": intake.patient_id,
            "structured_summary": case_summary,
            "routing_decision": care_path,
            "next_touchpoint": follow_up
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/check-in", summary="Evaluate a post-discharge check-in")
async def recovery_check_in(check_in: RecoveryCheckIn):
    """
    Deterministic demo routing keeps the prototype fast and auditable.
    It does not diagnose or replace a clinician.
    """
    notes = check_in.notes.lower()
    emergency_phrases = (
        "chest pain",
        "can't breathe",
        "cannot breathe",
        "struggling to breathe",
        "severe bleeding",
        "fainted",
        "unconscious",
        "new confusion",
    )
    red_flags = [phrase for phrase in emergency_phrases if phrase in notes]

    if red_flags:
        status = "urgent"
        headline = "Urgent help recommended"
        message = (
            "Your update mentions a possible emergency warning sign. "
            "Call 999/112 now or ask someone nearby to help."
        )
        next_actions = [
            "Call 999/112 now",
            "Do not drive yourself",
            "Keep your discharge paperwork and medicines nearby",
        ]
        follow_up = "Emergency escalation"
    elif (
        (check_in.temperature_c is not None and check_in.temperature_c >= 38)
        or check_in.pain_score >= 8
        or (
            check_in.symptom_change == "worse"
            and check_in.medication_status in {"some", "none", "not_sure"}
        )
    ):
        status = "review"
        headline = "A care-team review is recommended"
        message = (
            "One or more answers need a clinician to review them. "
            "This demo has prepared a concise handoff."
        )
        next_actions = [
            "Contact the ward or discharge number on your paperwork",
            "Share the prepared update with your care team",
            "If symptoms become severe, call 999/112",
        ]
        follow_up = "Clinician callback within 2 hours"
    else:
        status = "on_track"
        headline = "Your recovery check-in looks on track"
        message = (
            "No urgent rule was triggered by this update. "
            "Continue your discharge plan and complete the next check-in."
        )
        next_actions = [
            "Continue the medicines listed in your discharge plan",
            "Keep monitoring for new or worsening symptoms",
            "Complete tomorrow's 60-second check-in",
        ]
        follow_up = "Next check-in tomorrow at 09:00"

    medication_label = {
        "all": "All medicines taken",
        "some": "Some medicines missed",
        "none": "No medicines taken",
        "not_sure": "Medication instructions unclear",
    }[check_in.medication_status]
    temperature = (
        f"{check_in.temperature_c:.1f} °C"
        if check_in.temperature_c is not None
        else "Not provided"
    )

    return {
        "status": status,
        "headline": headline,
        "message": message,
        "next_actions": next_actions,
        "follow_up": follow_up,
        "care_team_summary": (
            f"Recovery day {check_in.recovery_day}. Symptoms: "
            f"{check_in.symptom_change}. Pain: {check_in.pain_score}/10. "
            f"Temperature: {temperature}. {medication_label}. "
            f"Patient note: {check_in.notes or 'None provided'}."
        ),
        "safety_note": (
            "Relay72 is a prototype, not a medical device. It does not diagnose "
            "or replace professional care."
        ),
    }

# Run locally using: uvicorn app.main:app --reload
