from pathlib import Path
from groq import Groq

import config

def create_groq_client() -> Groq:
    if not config.GROQ_API_KEY:
        raise RuntimeError("Missing Groq API key in configuration.")
    return Groq(api_key=config.GROQ_API_KEY)

def transcribe_audio(client: Groq, file_path: Path) -> str:
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

def format_transcript(client: Groq, raw_transcript: str) -> str:
    if not raw_transcript.strip():
        return raw_transcript

    print("[Formatter] Formatting transcript...", flush=True)
    try:
        response = client.chat.completions.create(
            model=config.FORMATTER_MODEL,
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS,
            messages=[
                {"role": "system", "content": config.FORMATTER_SYSTEM_PROMPT},
                {"role": "user", "content": raw_transcript},
            ],
        )
        formatted = (response.choices[0].message.content or "").strip()
    except Exception as exc:
        print(f"Formatter failed, returning raw transcript: {exc}", flush=True)
        return raw_transcript

    return formatted or raw_transcript
