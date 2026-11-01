# WayType

WayType is a Linux Wayland voice-typing utility. It uses the Voxora Python
SDK as its sole speech-to-text engine and keeps desktop integration in the
WayType application.

## Features

- Microphone capture, VAD, Groq Whisper transcription, and optional transcript
  formatting through Voxora.
- Clipboard copying with `wl-copy`.
- Keyboard simulation with `evdev` where required to paste into the focused
  application.
- GTK3 system-tray daemon with desktop notifications and audio feedback.
- GUI settings for formatting, recording mode, silence cutoff, sounds, and
  notifications.

## Tech stack

| Area | Technology |
| --- | --- |
| Speech-to-text | Voxora SDK with Groq Whisper |
| Audio and VAD | Voxora, PyAudio, WebRTC VAD |
| Desktop | Linux, Wayland, GTK3, Ayatana AppIndicator |
| Clipboard | `wl-copy` from `wl-clipboard` |
| Keyboard input | `evdev` |
| Notifications and sounds | GTK/ libnotify and `paplay` |

## Prerequisites

Install the system packages used by WayType's desktop integration:

```bash
sudo apt install wl-clipboard pulseaudio-utils \
  python3-gi gir1.2-gtk-3.0 gir1.2-ayatanaappindicator3-0.1
```

Use Python 3.10 or newer. Voxora, PyAudio, WebRTC VAD, Groq, OpenAI-compatible
formatting support, `python-dotenv`, and `evdev` are installed from
`requirements.txt`.

## Installation

```bash
git clone https://github.com/prakhar-thecoder/WayType.git
cd WayType
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

The requirements file installs the published `voxora` package from PyPI; a
separate Voxora checkout is not required.

Configure the Groq key:

```bash
cp .env.example .env
# Edit .env and set GROQ_API_KEY
```

## Configuration

The GTK daemon persists user-facing settings in `settings.json`:

| Setting | Effect |
| --- | --- |
| `format_text` | Enables or disables Voxora transcript formatting. |
| `listen_indefinitely` | Uses manual start/stop recording controlled by the existing stop-file workflow. |
| `silence_timeout` | Sets the VAD silence cutoff when automatic recording is enabled. |
| `play_sounds` | Enables or disables audio feedback. |
| `show_notifications` | Enables or disables desktop notifications. |

Advanced Voxora defaults are read from `.env` by `config.py`:

```text
GROQ_API_KEY              Required Groq API key
WHISPER_MODEL             Whisper model, default: whisper-large-v3-turbo
STT_LANGUAGE              Optional language hint; use this name in `.env`
VAD_MODE                  WebRTC VAD mode, default: 2
SAMPLE_RATE               Capture rate, default: 16000
FRAME_DURATION_MS         Frame duration, default: 20
PRE_SPEECH_DURATION       Pre-speech buffer, default: 0.3
MAX_RECORDING_DURATION    Maximum automatic recording duration, default: 300
SPEECH_START_TIMEOUT      Initial speech timeout, default: 10
FORMAT_BASE_URL           Compatible formatter endpoint
FORMAT_MODEL              Formatter model, default: openai/gpt-oss-120b
FORMAT_API_KEY            Optional formatter key; falls back to GROQ_API_KEY
PASTE_DELAY_SECONDS       Delay before keyboard simulation, default: 0.05
```

Audio is sent to Groq's cloud API for transcription. Formatting, when enabled,
receives the transcript after transcription and requires a compatible network
endpoint.

If `.env.example` contains `LANGUAGE`, rename that key to `STT_LANGUAGE`; the
runtime configuration uses `STT_LANGUAGE`.

## GTK daemon

The systemd unit starts only the GTK tray daemon. It does not run the dictation
pipeline; the global shortcut launches `run.sh`.

Install the unit using the current checkout path rather than assuming a fixed
home directory:

```bash
WAYTYPE_DIR="$(pwd)"
mkdir -p ~/.config/systemd/user
sed "s|/home/prakhar/Projects/WayType|$WAYTYPE_DIR|g" \
  systemd/waytype-daemon.service \
  > ~/.config/systemd/user/waytype-daemon.service
systemctl --user daemon-reload
systemctl --user enable waytype-daemon.service
systemctl --user start waytype-daemon.service
```

The unit uses `$WAYTYPE_DIR/venv/bin/python` and `$WAYTYPE_DIR` as its working
directory after the substitution. If the service is already active and the
unit changed, reload it and restart it deliberately rather than interrupting
an active desktop session unexpectedly.

## Keyboard shortcut

Add a desktop custom shortcut for:

```text
/absolute/path/to/WayType/run.sh
```

For example, bind it to `Super+H`. A second activation stops an active
“listen indefinitely” session through WayType's existing stop-file workflow.

## Project structure

```text
WayType/
├── main.py                         # Dictation entry point
├── config.py                       # Environment-backed Voxora defaults
├── run.sh                          # Activates venv and runs main.py
├── settings.json                   # GUI/user settings
├── core/
│   ├── pipeline.py                 # Voxora orchestration and desktop flow
│   ├── settings.py                 # settings.json load/save
│   ├── ipc.py                      # GTK daemon state notifications
│   └── context.py                  # Reserved runtime context
├── output/
│   └── clipboard.py                # wl-copy and evdev paste
├── ui/
│   └── daemon.py                   # GTK system-tray daemon
├── assets/                         # Audio feedback files
└── systemd/
    └── waytype-daemon.service      # User service template
```

WayType does not contain a second microphone, VAD, transcription, or formatter
implementation; those responsibilities belong to Voxora.
