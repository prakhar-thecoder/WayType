import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", "16000"))
CHANNELS = int(os.getenv("CHANNELS", "1"))
SAMPLE_WIDTH_BYTES = int(os.getenv("SAMPLE_WIDTH_BYTES", "2"))
FRAME_DURATION_MS = int(os.getenv("FRAME_DURATION_MS", "20"))
CHUNK_SIZE = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)
PRE_SPEECH_DURATION = float(os.getenv("PRE_SPEECH_DURATION", "0.5"))
VAD_MODE = int(os.getenv("VAD_MODE", "2"))
PASTE_DELAY_SECONDS = float(os.getenv("PASTE_DELAY_SECONDS", "0.05"))

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "whisper-large-v3-turbo")
FORMATTER_MODEL = os.getenv("FORMATTER_MODEL", "openai/gpt-oss-120b")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "8192"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.0"))

TEMP_FILE_PREFIX = "waytype_"
TEMP_FILE_SUFFIX = ".wav"

