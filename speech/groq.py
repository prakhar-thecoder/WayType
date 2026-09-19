"""
speech/groq.py

Groq-specific Whisper transcription.

Responsibilities:
  - Accept an already-constructed Groq client (created by the pipeline)
  - Upload the WAV file to Groq Whisper
  - Return the raw transcript string
  - Raise RuntimeError on failure

The Groq client is injected by the caller (core/pipeline.py) so that
exactly one client is created per invocation. This module must not
create its own Groq client.

Dependencies: config (model name only) — must not depend on ui, output,
or processing.
"""

from pathlib import Path

from groq import Groq

import config


def create_groq_client() -> Groq:
    """Construct and return a Groq client using the configured API key.

    Called once from the pipeline. Not called from other modules.
    """
    if not config.GROQ_API_KEY:
        raise RuntimeError("Missing Groq API key in configuration.")
    return Groq(api_key=config.GROQ_API_KEY)


def transcribe_audio(client: Groq, file_path: Path) -> str:
    """Transcribe a WAV file using Groq Whisper.

    Args:
        client: An already-constructed Groq client.
        file_path: Path to the temporary WAV file.

    Returns:
        The raw transcript string (stripped).

    Raises:
        RuntimeError: If the transcription API call fails.
    """
    print("[Whisper] Uploading to Whisper...", flush=True)
    try:
        with file_path.open("rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=audio_file,
                model=config.WHISPER_MODEL,
                response_format="text",
            )
    except Exception as exc:
        raise RuntimeError(f"Whisper transcription failed: {exc}") from exc

    return str(transcription).strip()
