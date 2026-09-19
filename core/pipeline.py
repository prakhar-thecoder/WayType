"""
core/pipeline.py

Central orchestration for the WayType dictation pipeline.

Reproduces the exact control flow previously in main.py:
  1. PID-based single-instance guard (sends stop to running instance)
  2. Load settings
  3. Construct Groq client (single instance, passed to speech/processing)
  4. Create VAD
  5. Notify GUI: listening
  6. Record audio (VAD-driven, respects listen_indefinitely / silence_timeout)
  7. Trim audio
  8. Save temporary WAV
  9. Transcribe with Whisper
  10. Optionally format transcript
  11. Notify GUI: pasting
  12. Paste text via Wayland clipboard
  13. Notify GUI: idle
  14. Cleanup (PID file, stop file, temp WAV)

Latency is logged at each major phase boundary.

Dependencies: audio, speech, processing, output, core.settings, core.ipc.
Must not depend on ui/ implementation details.
"""

import os
import time
from contextlib import suppress
from pathlib import Path

from audio import audio
from speech import groq as speech_groq
from processing import formatter
from output import clipboard
from core import ipc
from core import settings as settings_module

_PID_FILE = Path("/tmp/waytype.pid")
_STOP_FILE = Path("/tmp/waytype.stop")


def run() -> int:
    """Execute the full dictation pipeline.

    Returns:
        0 on success, 1 on recoverable failure, 130 on KeyboardInterrupt.
    """
    # --- PID guard: if already running, send stop signal and exit ---
    if _PID_FILE.exists():
        try:
            with open(_PID_FILE, "r") as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)  # Check if process exists
            _STOP_FILE.touch()
            print("Stop signal sent to running instance.", flush=True)
            return 0
        except (ProcessLookupError, ValueError):
            pass

    temp_path: Path | None = None

    try:
        with open(_PID_FILE, "w") as f:
            f.write(str(os.getpid()))

        settings = settings_module.load()
        format_text = settings.get("format_text", True)
        listen_indefinitely = settings.get("listen_indefinitely", False)
        silence_timeout = settings.get("silence_timeout", 1.0)

        # Single Groq client for the entire pipeline run
        client = speech_groq.create_groq_client()
        vad = audio.create_vad()

        ipc.notify_gui(ipc.STATE_LISTENING)
        t0 = time.time()
        recorded_frames = audio.record_until_silence(
            vad,
            listen_indefinitely=listen_indefinitely,
            silence_timeout=silence_timeout,
        )

        with suppress(FileNotFoundError):
            _PID_FILE.unlink()

        t1 = time.time()
        print(f"[Latency] Recording took {t1 - t0:.2f}s", flush=True)

        ipc.notify_gui(ipc.STATE_PROCESSING)
        trimmed_frames = audio.trim_audio(recorded_frames, vad)
        if not trimmed_frames:
            print("No speech detected.", flush=True)
            ipc.notify_gui(ipc.STATE_IDLE)
            return 1

        temp_path = audio.create_temp_wav_path()
        audio.save_wav(trimmed_frames, temp_path)
        t2 = time.time()
        print(f"[Latency] Trimming & saving took {t2 - t1:.2f}s", flush=True)

        raw_transcript = speech_groq.transcribe_audio(client, temp_path)
        if not raw_transcript:
            print("Whisper returned an empty transcript.", flush=True)
            ipc.notify_gui(ipc.STATE_IDLE)
            return 1
        t3 = time.time()
        print(f"[Latency] Transcription took {t3 - t2:.2f}s", flush=True)

        if format_text:
            final_transcript = formatter.format_transcript(client, raw_transcript)
        else:
            final_transcript = raw_transcript

        t4 = time.time()
        print(f"[Latency] Formatting took {t4 - t3:.2f}s", flush=True)

        print("\n--- Result ---", flush=True)
        print(final_transcript, flush=True)

        ipc.notify_gui(ipc.STATE_PASTING)
        clipboard.paste_text(final_transcript)
        t5 = time.time()
        print(f"[Latency] Typing took {t5 - t4:.2f}s", flush=True)
        print(f"[Latency] Total processing (post-recording) took {t5 - t1:.2f}s", flush=True)

        ipc.notify_gui(ipc.STATE_IDLE)
        return 0

    except KeyboardInterrupt:
        print("Cancelled.", flush=True)
        ipc.notify_gui(ipc.STATE_IDLE)
        return 130
    except RuntimeError as exc:
        print(f"Error: {exc}", flush=True)
        ipc.notify_gui(ipc.STATE_IDLE)
        return 1
    except Exception as exc:
        print(f"Unexpected error: {exc}", flush=True)
        ipc.notify_gui(ipc.STATE_IDLE)
        return 1
    finally:
        with suppress(FileNotFoundError):
            _PID_FILE.unlink()
        with suppress(FileNotFoundError):
            _STOP_FILE.unlink()
        audio.cleanup(temp_path)
