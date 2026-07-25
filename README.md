# Relay72 MVP

Relay72 is a focused 72-hour post-discharge safety-net prototype. It turns a
discharge plan into short recovery check-ins, an understandable next action,
and a concise care-team handoff.

This wedge is intentionally narrower than a general AI health companion:

- one workflow: the first days after leaving hospital;
- structured, auditable routing before generative AI;
- patient and care-team handoff in the same interaction;
- useful without wearable, EHR, voice, or scheduling integrations.

The current prototype also supports an optional recorded voice note. Audio is
uploaded to a server-only endpoint and transcribed with ElevenLabs Scribe v2;
the API key is never exposed to the browser.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## Prototype boundaries

The check-in route uses a transparent deterministic rule set for the demo. It
does not diagnose, continuously monitor a patient, or replace professional
care. The existing OpenAI intake endpoint requires `OPENAI_API_KEY`.
Voice transcription requires `ELEVENLABS_API_KEY`. Configure both as Vercel
environment variables and never commit them to GitHub.
