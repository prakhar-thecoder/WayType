import os
import time
import socket
import json
from pathlib import Path
from contextlib import suppress

import audio
import transcription
import wayland_typing

def notify_gui(state: str) -> None:
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect("/tmp/waytype_gui.sock")
        sock.sendall(json.dumps({"state": state}).encode("utf-8"))
        sock.close()
    except Exception:
        pass

def load_settings() -> dict:
    settings_file = Path(__file__).resolve().parent / "settings.json"
    if settings_file.exists():
        try:
            with open(settings_file, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def main() -> int:
    pid_file = Path("/tmp/waytype.pid")
    stop_file = Path("/tmp/waytype.stop")
    
    if pid_file.exists():
        try:
            with open(pid_file, "r") as f:
                pid = int(f.read().strip())
            os.kill(pid, 0) # Check if process exists
            stop_file.touch()
            print("Stop signal sent to running instance.", flush=True)
            return 0
        except (ProcessLookupError, ValueError):
            pass

    temp_path: Path | None = None

    try:
        with open(pid_file, "w") as f:
            f.write(str(os.getpid()))

        settings = load_settings()
        format_text = settings.get("format_text", True)

        client = transcription.create_groq_client()
        vad = audio.create_vad()

        notify_gui("listening")
        t0 = time.time()
        recorded_frames = audio.record_until_silence(vad)
        
        with suppress(FileNotFoundError):
            pid_file.unlink()
            
        t1 = time.time()
        print(f"[Latency] Recording took {t1 - t0:.2f}s", flush=True)

        notify_gui("processing")
        trimmed_frames = audio.trim_audio(recorded_frames, vad)
        if not trimmed_frames:
            print("No speech detected.", flush=True)
            notify_gui("idle")
            return 1

        temp_path = audio.create_temp_wav_path()
        audio.save_wav(trimmed_frames, temp_path)
        t2 = time.time()
        print(f"[Latency] Trimming & saving took {t2 - t1:.2f}s", flush=True)

        raw_transcript = transcription.transcribe_audio(client, temp_path)
        if not raw_transcript:
            print("Whisper returned an empty transcript.", flush=True)
            notify_gui("idle")
            return 1
        t3 = time.time()
        print(f"[Latency] Transcription took {t3 - t2:.2f}s", flush=True)

        if format_text:
            final_transcript = transcription.format_transcript(client, raw_transcript)
        else:
            final_transcript = raw_transcript
            
        t4 = time.time()
        print(f"[Latency] Formatting took {t4 - t3:.2f}s", flush=True)

        print("\n--- Result ---", flush=True)
        print(final_transcript, flush=True)
        
        notify_gui("pasting")
        wayland_typing.type_text(final_transcript)
        t5 = time.time()
        print(f"[Latency] Typing took {t5 - t4:.2f}s", flush=True)
        print(f"[Latency] Total processing (post-recording) took {t5 - t1:.2f}s", flush=True)
        
        notify_gui("idle")
        return 0
    except KeyboardInterrupt:
        print("Cancelled.", flush=True)
        notify_gui("idle")
        return 130
    except RuntimeError as exc:
        print(f"Error: {exc}", flush=True)
        notify_gui("idle")
        return 1
    except Exception as exc:
        print(f"Unexpected error: {exc}", flush=True)
        notify_gui("idle")
        return 1
    finally:
        with suppress(FileNotFoundError):
            pid_file.unlink()
        with suppress(FileNotFoundError):
            stop_file.unlink()
        audio.cleanup(temp_path)

if __name__ == "__main__":
    raise SystemExit(main())