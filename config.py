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
SILENCE_TIMEOUT = float(os.getenv("SILENCE_TIMEOUT", "1"))
VAD_MODE = int(os.getenv("VAD_MODE", "2"))
PASTE_DELAY_SECONDS = float(os.getenv("PASTE_DELAY_SECONDS", "0.05"))

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "whisper-large-v3-turbo")
FORMATTER_MODEL = os.getenv("FORMATTER_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "8192"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.0"))

TEMP_FILE_PREFIX = "waytype_"
TEMP_FILE_SUFFIX = ".wav"

FORMATTER_SYSTEM_PROMPT = """
    You are a transcript formatter for speech recognition output. Your only job is to restore punctuation, capitalization, and paragraph breaks. Do not rewrite, summarize, paraphrase, shorten, expand, or reorder anything. Preserve every spoken word and preserve the original meaning exactly. Preserve filenames, URLs, code snippets, programming language names, package names, CLI commands, shell commands, API names, function names, class names, variable names, and numbers exactly. Only fix obvious transcription errors when you are extremely confident. Return only the corrected transcript and nothing else.
""" 