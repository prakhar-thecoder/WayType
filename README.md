# WayType 🎙️

**The lightning-fast `Windows + H` voice typing alternative for Ubuntu & Wayland.**

WayType is a modular, high-performance voice dictation engine designed specifically for modern Linux desktops. It leverages the blazingly fast Groq Whisper API to transcribe your speech instantly, formats it using LLaMA, and securely injects the text directly into whatever application you're focused on using native Wayland kernel-level inputs.

It brings a completely seamless, keyboard-shortcut-driven voice typing experience to Linux, complete with a background system tray daemon and non-intrusive 3-state audio feedback.

## ✨ Features
- **Native Wayland Support**: Safely uses `wl-copy` and `evdev` to paste text directly, bypassing the limitations of traditional X11 macro tools on Wayland.
- **Ultra-Low Latency**: Uses Groq's insanely fast Whisper API. Dictation often appears on your screen within *milliseconds* of you finishing your sentence.
- **Auto-Formatting**: Uses LLaMA to intelligently add punctuation and capitalization to your raw speech before pasting.
- **Background Daemon**: A lightweight GTK3 System Tray indicator that visually shows whether you are idle, listening, or processing.
- **Asynchronous Audio Feedback**: Plays built-in Ubuntu system sounds instantly (`bell`, `message`, `complete`) to guide you without stealing focus.

## 🛠 Prerequisites

Ensure you have the following system dependencies installed on Ubuntu:

```bash
# Core Wayland and Audio tools
sudo apt install wl-clipboard pulseaudio-utils

# GTK dependencies for the System Tray daemon
sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-ayatanaappindicator3-0.1
```

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/prakhar-thecoder/WayType.git
   cd WayType
   ```

2. **Set up the Python Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure your API Key:**
   ```bash
   cp .env.example .env
   # Edit .env and insert your Groq API Key
   nano .env
   ```

## 🖥 Setting up the Background Daemon

To get the System Tray icon and audio feedback, run the daemon as a systemd user service so it starts automatically in the background.

1. **Copy the provided service file:**
   ```bash
   mkdir -p ~/.config/systemd/user/
   cp systemd/waytype-daemon.service ~/.config/systemd/user/
   ```

2. *(Optional)* If you cloned WayType to a location other than `/home/prakhar/Projects/voice-typing`, edit the `ExecStart` and `WorkingDirectory` paths in `~/.config/systemd/user/waytype-daemon.service`.

3. **Enable and start the service:**
   ```bash
   systemctl --user daemon-reload
   systemctl --user enable --now waytype-daemon.service
   ```

## ⌨️ Creating the Global Keyboard Shortcut

To make it behave just like `Win + H`:

1. Open Ubuntu **Settings** > **Keyboard** > **View and Customize Shortcuts** > **Custom Shortcuts**.
2. Click **Add Shortcut**.
3. **Name**: `WayType Voice Dictation`
4. **Command**: `/absolute/path/to/waytype/run.sh` *(Make sure to use your actual path)*
5. **Shortcut**: Press `Super + H` (or whatever you prefer!).
6. Click **Add**.

**You're done!** Press your shortcut anywhere in your OS to trigger the mic. You'll hear a bell ping, the tray icon will change, and you can start speaking.

## ⚙️ Customization

- **Audio Alerts**: If you want to use custom `.wav` files instead of Ubuntu's default sounds, you can edit the paths in `gui_daemon.py` or place your sounds in an `assets/` folder.
- **Delays**: Adjust `PASTE_DELAY_SECONDS` in `config.py` if your text editor is dropping characters or missing the paste event.
- **Silence Detection**: Tweak `SILENCE_DURATION_SECONDS` in `config.py` to change how long the script waits for you to stop talking.
