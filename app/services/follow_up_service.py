from app.models.schemas import FollowUpMessage

def trigger_follow_up(patient_id: str, care_path: str):
    # MVP Mock: Simulates sending a follow-up SMS or chat push notification
    # In production, this could schedule a cron job, Celery task, or trigger Twilio
    
    message = f"Hi there, checking in on your {care_path}. Are your symptoms improving?"
    
    # Save to DB and push to chat interface
    print(f"[CONTINUOUS COMPANION] Sent to {patient_id}: {message}")
    
    return FollowUpMessage(
        patient_id=patient_id,
        message=message,
        channel="chat"
    )
