from pathlib import Path

import audio
import transcription
import wayland_typing

def main() -> int:
    temp_path: Path | None = None

    try:
        client = transcription.create_groq_client()
        vad = audio.create_vad()

        recorded_frames = audio.record_until_silence(vad)
        trimmed_frames = audio.trim_audio(recorded_frames, vad)

        if not trimmed_frames:
            print("No speech detected.", flush=True)
            return 1

        temp_path = audio.create_temp_wav_path()
        audio.save_wav(trimmed_frames, temp_path)

        raw_transcript = transcription.transcribe_audio(client, temp_path)
        if not raw_transcript:
            print("Whisper returned an empty transcript.", flush=True)
            return 1

        final_transcript = transcription.format_transcript(client, raw_transcript)

        print("\n--- Result ---", flush=True)
        print(final_transcript, flush=True)
        
        wayland_typing.type_text(final_transcript)
        
        return 0
    except KeyboardInterrupt:
        print("Cancelled.", flush=True)
        return 130
    except RuntimeError as exc:
        print(f"Error: {exc}", flush=True)
        return 1
    except Exception as exc:
        print(f"Unexpected error: {exc}", flush=True)
        return 1
    finally:
        audio.cleanup(temp_path)

if __name__ == "__main__":
    raise SystemExit(main())