import os
import sys
import wave
import tempfile
from collections import deque
from contextlib import suppress
from pathlib import Path
from typing import Deque, Sequence

class SuppressAlsaErr:
    def __enter__(self):
        self.devnull = os.open(os.devnull, os.O_WRONLY)
        self.old_stderr = os.dup(sys.stderr.fileno())
        sys.stderr.flush()
        os.dup2(self.devnull, sys.stderr.fileno())

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stderr.flush()
        os.dup2(self.old_stderr, sys.stderr.fileno())
        os.close(self.old_stderr)
        os.close(self.devnull)

import pyaudio
import webrtcvad

import config

def create_vad() -> webrtcvad.Vad:
    vad = webrtcvad.Vad()
    vad.set_mode(config.VAD_MODE)
    return vad

def create_temp_wav_path() -> Path:
    with tempfile.NamedTemporaryFile(
        prefix=config.TEMP_FILE_PREFIX,
        suffix=config.TEMP_FILE_SUFFIX,
        delete=False,
    ) as temp_file:
        return Path(temp_file.name)

def save_wav(frames: Sequence[bytes], file_path: Path) -> None:
    with wave.open(str(file_path), "wb") as wav_file:
        wav_file.setnchannels(config.CHANNELS)
        wav_file.setsampwidth(config.SAMPLE_WIDTH_BYTES)
        wav_file.setframerate(config.SAMPLE_RATE)
        wav_file.writeframes(b"".join(frames))

def trim_audio(frames: Sequence[bytes], vad: webrtcvad.Vad) -> list[bytes]:
    if not frames:
        return []

    speech_flags = [vad.is_speech(frame, config.SAMPLE_RATE) for frame in frames]
    if not any(speech_flags):
        return []

    first_speech_index = next(index for index, is_speech in enumerate(speech_flags) if is_speech)
    last_speech_index = len(speech_flags) - 1 - next(
        index for index, is_speech in enumerate(reversed(speech_flags)) if is_speech
    )
    return list(frames[first_speech_index : last_speech_index + 1])

def record_until_silence(vad: webrtcvad.Vad) -> list[bytes]:
    pre_speech_frames = max(1, int(config.PRE_SPEECH_DURATION * 1000 / config.FRAME_DURATION_MS))
    pre_buffer: Deque[bytes] = deque(maxlen=pre_speech_frames)
    recorded_frames: list[bytes] = []
    is_recording = False
    silent_frame_count = 0
    silence_frame_limit = max(1, int(config.SILENCE_TIMEOUT * 1000 / config.FRAME_DURATION_MS))

    with SuppressAlsaErr():
        audio = pyaudio.PyAudio()
    stream = None

    print("[Audio] Listening...", flush=True)

    try:
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=config.CHANNELS,
            rate=config.SAMPLE_RATE,
            input=True,
            frames_per_buffer=config.CHUNK_SIZE,
        )

        while True:
            try:
                frame = stream.read(config.CHUNK_SIZE, exception_on_overflow=False)
            except OSError as exc:
                raise RuntimeError("Failed reading from the microphone.") from exc

            is_speech = vad.is_speech(frame, config.SAMPLE_RATE)

            if not is_recording:
                pre_buffer.append(frame)
                if is_speech:
                    print("[Audio] Speech detected...", flush=True)
                    print("[Audio] Recording...", flush=True)
                    is_recording = True
                    recorded_frames.extend(pre_buffer)
                    silent_frame_count = 0
                continue

            recorded_frames.append(frame)

            if is_speech:
                silent_frame_count = 0
                continue

            silent_frame_count += 1
            if silent_frame_count >= silence_frame_limit:
                print("[Audio] Silence detected.", flush=True)
                break
    except OSError as exc:
        raise RuntimeError(f"Audio device error: {exc}") from exc
    finally:
        if stream is not None:
            with suppress(Exception):
                stream.stop_stream()
            with suppress(Exception):
                stream.close()
        with suppress(Exception):
            audio.terminate()

    return recorded_frames

def cleanup(temp_path: Path | None) -> None:
    if temp_path is None:
        return

    with suppress(FileNotFoundError, OSError):
        temp_path.unlink()
