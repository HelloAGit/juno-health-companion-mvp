from fastapi import FastAPI, HTTPException
from app.models.schemas import PatientIntake
from app.services.openai_service import generate_structured_summary
from app.services.juno_service import route_to_care_path
from app.services.follow_up_service import trigger_follow_up

app = FastAPI(title="Health Companion MVP API")

@app.post("/api/v1/intake", summary="Process Voice Intake and Route")
async process_intake(intake: PatientIntake):
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

# Run locally using: uvicorn app.main:app --reload
