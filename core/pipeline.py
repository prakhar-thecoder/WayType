"""WayType application orchestration using Voxora for speech-to-text."""

import os
import time
from contextlib import suppress
from pathlib import Path

from voxora import STT
from voxora.exceptions import VoxoraError

from output import clipboard
from core import ipc
from core import settings as settings_module
import config


_PID_FILE = Path("/tmp/waytype.pid")
_STOP_FILE = Path("/tmp/waytype.stop")


def _create_stt(settings: dict, *, manual: bool) -> STT:
    """Create the Voxora engine from WayType settings and environment config."""
    return STT(
        engine="groq",
        api_key=config.GROQ_API_KEY or None,
        stt_model=config.WHISPER_MODEL,
        language=config.STT_LANGUAGE,
        vad=not manual,
        vad_mode=config.VAD_MODE,
        silence_duration=settings.get("silence_timeout", 1.0),
        pre_speech_duration=config.PRE_SPEECH_DURATION,
        sample_rate=config.SAMPLE_RATE,
        frame_duration_ms=config.FRAME_DURATION_MS,
        max_recording_duration=config.MAX_RECORDING_DURATION if not manual else None,
        speech_start_timeout=config.SPEECH_START_TIMEOUT,
        format=settings.get("format_text", config.FORMAT_TEXT_DEFAULT),
        format_base_url=config.FORMAT_BASE_URL,
        format_model=config.FORMAT_MODEL,
        format_api_key=config.FORMAT_API_KEY,
    )


def _wait_for_manual_stop() -> None:
    while not _STOP_FILE.exists():
        time.sleep(0.05)
    with suppress(FileNotFoundError):
        _STOP_FILE.unlink()


def run() -> int:
    """Run one WayType dictation request and paste its transcript."""
    if _PID_FILE.exists():
        try:
            with open(_PID_FILE, "r") as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)
            _STOP_FILE.touch()
            print("Stop signal sent to running instance.", flush=True)
            return 0
        except (ProcessLookupError, ValueError):
            pass

    stt = None
    manual_recording = False
    try:
        with open(_PID_FILE, "w") as f:
            f.write(str(os.getpid()))

        settings = settings_module.load()
        manual = settings.get("listen_indefinitely", False)
        stt = _create_stt(settings, manual=manual)

        ipc.notify_gui(ipc.STATE_LISTENING)
        started_at = time.monotonic()
        if manual:
            stt.start()
            manual_recording = True
            _wait_for_manual_stop()
            transcript = stt.stop()
            manual_recording = False
        else:
            transcript = stt.listen()
        print(f"[Latency] Recording and transcription took {time.monotonic() - started_at:.2f}s", flush=True)

        ipc.notify_gui(ipc.STATE_PROCESSING)
        print("\n--- Result ---", flush=True)
        print(transcript, flush=True)
        ipc.notify_gui(ipc.STATE_PASTING)
        clipboard.paste_text(transcript)
        ipc.notify_gui(ipc.STATE_IDLE)
        return 0

    except KeyboardInterrupt:
        if manual_recording and stt is not None:
            with suppress(Exception):
                stt.stop()
        print("Cancelled.", flush=True)
        ipc.notify_gui(ipc.STATE_IDLE)
        return 130
    except VoxoraError as exc:
        print(f"Voxora error: {exc}", flush=True)
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
