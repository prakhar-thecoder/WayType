"""
processing/formatter.py

Normal transcript formatter using the Groq LLM.

Responsibilities:
  - Load the normal formatter system prompt from prompts/normal.json
  - Accept a raw transcript and an already-constructed Groq client
  - Invoke the LLM with the current model, temperature, and token settings
  - Parse the JSON response and return the formatted_text value
  - Fall back to the raw transcript on any failure

The Groq client is injected by the caller (core/pipeline.py) so that
exactly one client is created per invocation.

Dependencies: config (model/LLM settings) — must not depend on audio,
speech, ui, or output.
"""

import json
from pathlib import Path

from groq import Groq

import config

# Resolve prompts/normal.json relative to the repository root.
_REPO_ROOT = Path(__file__).resolve().parent.parent
_NORMAL_PROMPT_PATH = _REPO_ROOT / "prompts" / "normal.json"


def _load_normal_prompt() -> str:
    """Load the normal formatter system prompt from prompts/normal.json."""
    try:
        with open(_NORMAL_PROMPT_PATH, "r") as f:
            data = json.load(f)
        return data["system_prompt"]
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Failed to load normal formatter prompt: {exc}") from exc


def format_transcript(client: Groq, raw_transcript: str) -> str:
    """Format a raw Whisper transcript using the normal formatter prompt.

    Args:
        client: An already-constructed Groq client.
        raw_transcript: The raw text returned by Whisper.

    Returns:
        The formatted transcript string, or the raw transcript if formatting
        fails or produces an empty result.
    """
    if not raw_transcript.strip():
        return raw_transcript

    print("[Formatter] Formatting transcript...", flush=True)
    try:
        system_prompt = _load_normal_prompt()
        response = client.chat.completions.create(
            model=config.FORMATTER_MODEL,
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"<transcript>\n{raw_transcript}\n</transcript>"},
            ],
        )
        content = response.choices[0].message.content
        if content:
            parsed = json.loads(content)
            formatted = parsed.get("formatted_text", "").strip()
        else:
            formatted = ""
    except Exception as exc:
        print(f"Formatter failed, returning raw transcript: {exc}", flush=True)
        return raw_transcript

    return formatted or raw_transcript
