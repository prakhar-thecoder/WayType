# WayType 🎙️

**The lightning-fast `Windows + H` voice typing alternative for Wayland desktops.**

WayType is a modular, high-performance voice dictation engine designed for modern Linux desktops running Wayland. It leverages the blazingly fast Groq Whisper API to transcribe your speech, formats it using Llama, and securely injects the text directly into the application you're focused on using native Wayland-compatible input methods.

It brings a seamless, keyboard-shortcut-driven voice typing experience to Linux, complete with a lightweight background system tray daemon and non-intrusive 3-state audio feedback.

## ✨ Features

* **Native Wayland Support**: Safely uses `wl-copy` and `evdev` to paste text directly, bypassing the limitations of traditional X11 macro tools on Wayland.
* **Ultra-Low Latency**: Powered by Groq's incredibly fast Whisper API. Dictation typically appears almost instantly after you finish speaking.
* **Auto-Formatting**: Uses Llama to intelligently add punctuation and capitalization to your raw speech before pasting.
* **Background Daemon**: A lightweight GTK3 system tray indicator that visually shows whether WayType is idle, listening, or processing.
* **Asynchronous Audio Feedback**: Plays built-in Ubuntu system sounds (`bell`, `message`, `complete`) to guide you without stealing focus.

## 🛠 Prerequisites

Ensure you have the following system dependencies installed:

```bash
# Core Wayland and Audio tools
sudo apt install wl-clipboard pulseaudio-utils

# GTK dependencies for the System Tray daemon
sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-ayatanaappindicator3-0.1
```

## 🚀 Installation

> **Tested on Python 3.10.** Other Python versions may work but have not been officially tested.

1. **Clone the repository:**

```bash
git clone https://github.com/prakhar-thecoder/WayType.git
cd WayType
```

2. **Set up the Python virtual environment:**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Configure your API key:**

```bash
cp .env.example .env
# Edit .env and insert your Groq API Key
nano .env
```

## 🖥 Setting up the Background Daemon

To get the system tray icon and audio feedback, run the daemon as a systemd user service so it starts automatically in the background.

1. **Copy the provided service file:**

```bash
mkdir -p ~/.config/systemd/user/
cp systemd/waytype-daemon.service ~/.config/systemd/user/
```

2. **Update the service file paths.**

> **Important:** The provided `waytype-daemon.service` file contains the development paths from my machine (`/home/prakhar/Projects/WayType`). Before enabling the service, you **must** update both the `ExecStart` and `WorkingDirectory` entries to match the location where you cloned WayType.

3. **Enable and start the service:**

```bash
systemctl --user daemon-reload
systemctl --user enable --now waytype-daemon.service
```

## ⌨️ Creating the Global Keyboard Shortcut

To make it behave just like `Win + H`:

1. Open **Settings → Keyboard → View and Customize Shortcuts → Custom Shortcuts**.
2. Click **Add Shortcut**.
3. **Name:** `WayType Voice Dictation`
4. **Command:** `/absolute/path/to/WayType/run.sh` *(replace this with the actual path where you cloned the repository).*
5. **Shortcut:** Press `Super + H` (or any shortcut you prefer).
6. Click **Add**.

**You're done!** Press your shortcut anywhere in your desktop to trigger the microphone. You'll hear a bell, the tray icon will change state, and you can start speaking.

## ⚙️ Customization

WayType features an easy-to-use GTK GUI for configuring your experience. Just click the system tray icon and open **Settings** to access:
* **Format Text:** Toggle whether you want LLaMA to add punctuation and capitalization to your dictation, or just paste the raw Whisper output instantly.
* **Listen Indefinitely:** Toggle whether WayType should automatically stop recording when you stop speaking. If turned on, you can speak as slowly as you like—simply press your global shortcut (`Super + H`) a second time to instantly stop recording and paste!
* **Silence Cutoff:** If you prefer automatic cutoff, use this spinner to adjust exactly how many seconds of silence it takes to trigger the paste (from 0.5s to 10s).
* **Audio/Visual Feedback:** Toggle the playback of Ubuntu system sounds and native desktop notifications.

For advanced technical settings:
* **Audio Alerts:** Use your own `.wav` files by editing the paths in `gui_daemon.py` or placing your sounds inside an `assets/` folder.
* **Paste Delay:** Adjust `PASTE_DELAY_SECONDS` in `config.py` if your editor occasionally drops characters or misses the paste event.

## 💡 Why WayType?

After switching from Windows to Ubuntu, I found myself constantly missing the simplicity of the built-in **Win + H** voice typing experience.

WayType was built to bring that same keyboard-first workflow to modern Wayland desktops while keeping the experience lightweight, responsive, and privacy-conscious by only sending audio to the configured transcription service when you explicitly trigger it.
