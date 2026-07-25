import os
import json
from openai import OpenAI
from app.models.schemas import StructuredCaseSummary


def _get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY environment variable")
    return OpenAI(api_key=api_key)


def generate_structured_summary(transcript: str) -> StructuredCaseSummary:
    prompt = f"""
    Analyze the following patient transcript and extract the medical intake details.
    Respond ONLY with a JSON object containing: primary_symptom, duration, severity (1-10), and additional_notes.

    Transcript: \"{transcript}\"
    """

    client = _get_openai_client()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": prompt}],
        response_format={"type": "json_object"},
    )

    # Parse the JSON response into our Pydantic model
    data = json.loads(response.choices[0].message.content)
    return StructuredCaseSummary(**data)
