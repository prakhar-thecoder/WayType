import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
STT_LANGUAGE = os.getenv("STT_LANGUAGE") or None
VAD_MODE = int(os.getenv("VAD_MODE", "2"))
SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", "16000"))
FRAME_DURATION_MS = int(os.getenv("FRAME_DURATION_MS", "20"))
PRE_SPEECH_DURATION = float(os.getenv("PRE_SPEECH_DURATION", "0.3"))
MAX_RECORDING_DURATION = os.getenv("MAX_RECORDING_DURATION")
MAX_RECORDING_DURATION = float(MAX_RECORDING_DURATION) if MAX_RECORDING_DURATION else 300.0
SPEECH_START_TIMEOUT = os.getenv("SPEECH_START_TIMEOUT")
SPEECH_START_TIMEOUT = float(SPEECH_START_TIMEOUT) if SPEECH_START_TIMEOUT else 10.0
PASTE_DELAY_SECONDS = float(os.getenv("PASTE_DELAY_SECONDS", "0.05"))

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "whisper-large-v3-turbo")
FORMAT_TEXT_DEFAULT = os.getenv("FORMAT_TEXT", "true").lower() in {"1", "true", "yes", "on"}
FORMAT_BASE_URL = os.getenv("FORMAT_BASE_URL", "https://api.groq.com/openai/v1")
FORMAT_MODEL = os.getenv("FORMAT_MODEL", "openai/gpt-oss-120b")
FORMAT_API_KEY = os.getenv("FORMAT_API_KEY") or None

