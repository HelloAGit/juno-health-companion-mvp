import json
import os
from openai import OpenAI
from app.models.schemas import StructuredCaseSummary

def generate_structured_summary(transcript: str) -> StructuredCaseSummary:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    client = OpenAI(api_key=api_key)
    prompt = f"""
    Analyze the following patient transcript and extract the medical intake details.
    Respond ONLY with a JSON object containing: primary_symptom, duration, severity (1-10), and additional_notes.
    
    Transcript: "{transcript}"
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": prompt}],
        response_format={ "type": "json_object" }
    )
    
    # Parse the JSON response into our Pydantic model
    data = json.loads(response.choices[0].message.content)
    return StructuredCaseSummary(**data)
