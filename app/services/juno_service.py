from app.models.schemas import StructuredCaseSummary, CarePathRoute

def route_to_care_path(summary: StructuredCaseSummary) -> CarePathRoute:
    # MVP Mock: In production, this would be an HTTP POST to the Juno API
    # e.g., requests.post("https://api.juno.health/route", json=summary.dict())
    
    urgency = "high" if summary.severity >= 7 else "standard"
    action = "Telehealth appointment" if urgency == "standard" else "Urgent Care Visit"
    
    return CarePathRoute(
        route_id="juno_path_789",
        recommended_action=action,
        urgency_level=urgency
    )
