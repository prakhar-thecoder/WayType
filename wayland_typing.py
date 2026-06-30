import subprocess
import time
from evdev import UInput, ecodes as e

import config

def type_text(text: str) -> None:
    if not text:
        return

    try:
        # Copy to Wayland clipboard
        subprocess.run(["wl-copy"], input=text.encode("utf-8"), check=True)
        
        # Wait for user to focus the window if they haven't already
        time.sleep(config.PASTE_DELAY_SECONDS)
        
        # Inject Ctrl+V using native evdev
        with UInput() as ui:
            time.sleep(0.1) # Brief pause for uinput device to settle
            
            ui.write(e.EV_KEY, e.KEY_LEFTCTRL, 1) # Press Ctrl
            ui.syn()
            
            ui.write(e.EV_KEY, e.KEY_V, 1)        # Press V
            ui.syn()
            
            time.sleep(0.01)                      # Tiny delay to ensure OS registers combination
            
            ui.write(e.EV_KEY, e.KEY_V, 0)        # Release V
            ui.syn()
            
            ui.write(e.EV_KEY, e.KEY_LEFTCTRL, 0) # Release Ctrl
            ui.syn()
            
    except Exception as exc:
        print(f"[Typing] Failed to paste text: {exc}", flush=True)

if __name__ == "__main__":
    type_text("Hello Mike, how are you?")
