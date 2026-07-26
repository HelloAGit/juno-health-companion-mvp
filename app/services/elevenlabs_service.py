import os

import httpx


ELEVENLABS_TRANSCRIBE_URL = "https://api.elevenlabs.io/v1/speech-to-text"
MAX_AUDIO_BYTES = 10 * 1024 * 1024
ALLOWED_AUDIO_TYPES = {
    "audio/mp4",
    "audio/mpeg",
    "audio/ogg",
    "audio/wav",
    "audio/webm",
    "video/webm",
}


class TranscriptionConfigurationError(RuntimeError):
    pass


class TranscriptionRequestError(RuntimeError):
    pass


async def transcribe_audio(
    *,
    audio: bytes,
    filename: str,
    content_type: str,
) -> str:
    """Transcribe a short voice check-in without persisting the audio."""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise TranscriptionConfigurationError(
            "ELEVENLABS_API_KEY is not configured"
        )
    if not audio:
        raise TranscriptionRequestError("The audio recording is empty")
    if len(audio) > MAX_AUDIO_BYTES:
        raise TranscriptionRequestError("The audio recording exceeds 10 MB")

    # MediaRecorder MIME types often include codec parameters, such as
    # "audio/webm;codecs=opus". Validate and forward the container MIME type.
    normalized_content_type = content_type.split(";", 1)[0].strip().lower()
    if normalized_content_type not in ALLOWED_AUDIO_TYPES:
        raise TranscriptionRequestError("Unsupported audio format")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                ELEVENLABS_TRANSCRIBE_URL,
                headers={"xi-api-key": api_key},
                data={
                    "model_id": "scribe_v2",
                    "language_code": "eng",
                },
                files={
                    "file": (
                        filename or "relay72-check-in.webm",
                        audio,
                        normalized_content_type,
                    )
                },
            )
    except httpx.RequestError as exc:
        raise TranscriptionRequestError(
            "ElevenLabs could not be reached"
        ) from exc

    if response.status_code >= 400:
        raise TranscriptionRequestError(
            f"ElevenLabs transcription failed ({response.status_code})"
        )

    transcript = response.json().get("text", "").strip()
    if not transcript:
        raise TranscriptionRequestError(
            "No speech could be transcribed from the recording"
        )
    return transcript
