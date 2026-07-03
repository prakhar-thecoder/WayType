import os
import json
import socket
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

START_SOUND = ASSETS_DIR / "start.wav"
COMPLETE_SOUND = ASSETS_DIR / "complete.wav"

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AyatanaAppIndicator3', '0.1')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk, GLib, AyatanaAppIndicator3 as AppIndicator, Notify

SOCKET_PATH = "/tmp/waytype_gui.sock"
SETTINGS_FILE = BASE_DIR / "settings.json"

class VoiceTypingDaemon:
    def __init__(self):
        self.state = "idle"
        self.settings = {
            "play_sounds": True, 
            "show_notifications": True, 
            "format_text": True,
            "listen_indefinitely": False,
            "silence_timeout": 1.0
        }
        self.load_settings()
        
        Notify.init("WayType")

        # Setup AppIndicator
        self.indicator = AppIndicator.Indicator.new(
            "waytype-daemon",
            "audio-input-microphone-symbolic",
            AppIndicator.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self.menu = Gtk.Menu()
        
        settings_item = Gtk.MenuItem(label="Settings")
        settings_item.connect("activate", self.show_settings_window)
        self.menu.append(settings_item)
        
        quit_item = Gtk.MenuItem(label="Quit Daemon")
        quit_item.connect("activate", Gtk.main_quit)
        self.menu.append(quit_item)
        
        self.menu.show_all()
        self.indicator.set_menu(self.menu)

        # IPC Socket Setup
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)
            
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(SOCKET_PATH)
        self.server.listen(5)
        
        # Add watch to GTK main loop for incoming connections
        GLib.io_add_watch(self.server.fileno(), GLib.IO_IN, self.on_client_connect)
        
        self.update_ui("idle")

    def load_settings(self):
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, "r") as f:
                    self.settings.update(json.load(f))
            except Exception as e:
                print(f"Error loading settings: {e}")

    def save_settings(self):
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(self.settings, f)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def show_settings_window(self, widget):
        window = Gtk.Window(title="WayType Settings")
        window.set_default_size(300, 150)
        window.set_position(Gtk.WindowPosition.CENTER)
        window.set_border_width(20)
        
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        
        # Sounds Toggle
        sound_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        sound_label = Gtk.Label(label="Play Sounds")
        sound_switch = Gtk.Switch()
        sound_switch.set_active(self.settings.get("play_sounds", True))
        sound_switch.connect("notify::active", self.on_sound_toggled)
        sound_box.pack_start(sound_label, False, False, 0)
        sound_box.pack_end(sound_switch, False, False, 0)
        
        # Notifications Toggle
        notif_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        notif_label = Gtk.Label(label="Show Notifications")
        notif_switch = Gtk.Switch()
        notif_switch.set_active(self.settings.get("show_notifications", True))
        notif_switch.connect("notify::active", self.on_notif_toggled)
        notif_box.pack_start(notif_label, False, False, 0)
        notif_box.pack_end(notif_switch, False, False, 0)
        
        # Format Text Toggle
        format_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        format_label = Gtk.Label(label="Format Text")
        format_switch = Gtk.Switch()
        format_switch.set_active(self.settings.get("format_text", True))
        format_switch.connect("notify::active", self.on_format_toggled)
        format_box.pack_start(format_label, False, False, 0)
        format_box.pack_end(format_switch, False, False, 0)
        
        # Listen Indefinitely Toggle
        indef_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        indef_label = Gtk.Label(label="Listen Indefinitely (Double-tap to stop)")
        indef_switch = Gtk.Switch()
        indef_switch.set_active(self.settings.get("listen_indefinitely", False))
        indef_switch.connect("notify::active", self.on_indef_toggled)
        indef_box.pack_start(indef_label, False, False, 0)
        indef_box.pack_end(indef_switch, False, False, 0)

        # Silence Timeout Spinner
        silence_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        silence_label = Gtk.Label(label="Silence Cutoff (seconds)")
        silence_adj = Gtk.Adjustment(value=self.settings.get("silence_timeout", 1.0), lower=0.5, upper=10.0, step_increment=0.5, page_increment=1.0, page_size=0.0)
        self.silence_spin = Gtk.SpinButton(adjustment=silence_adj, numeric=True, digits=1)
        self.silence_spin.connect("value-changed", self.on_silence_changed)
        self.silence_spin.set_sensitive(not indef_switch.get_active())
        silence_box.pack_start(silence_label, False, False, 0)
        silence_box.pack_end(self.silence_spin, False, False, 0)
        
        vbox.pack_start(sound_box, False, False, 0)
        vbox.pack_start(notif_box, False, False, 0)
        vbox.pack_start(format_box, False, False, 0)
        vbox.pack_start(indef_box, False, False, 0)
        vbox.pack_start(silence_box, False, False, 0)
        
        window.add(vbox)
        window.show_all()

    def on_sound_toggled(self, switch, gparam):
        self.settings["play_sounds"] = switch.get_active()
        self.save_settings()

    def on_notif_toggled(self, switch, gparam):
        self.settings["show_notifications"] = switch.get_active()
        self.save_settings()

    def on_format_toggled(self, switch, gparam):
        self.settings["format_text"] = switch.get_active()
        self.save_settings()

    def on_indef_toggled(self, switch, gparam):
        is_active = switch.get_active()
        self.settings["listen_indefinitely"] = is_active
        self.silence_spin.set_sensitive(not is_active)
        self.save_settings()

    def on_silence_changed(self, spin_button):
        self.settings["silence_timeout"] = spin_button.get_value()
        self.save_settings()

    def on_client_connect(self, source, condition):
        client, addr = self.server.accept()
        GLib.io_add_watch(client.fileno(), GLib.IO_IN, self.on_client_message, client)
        return True # Keep listening

    def on_client_message(self, source, condition, client):
        try:
            data = client.recv(1024)
            if not data:
                client.close()
                return False
            
            payload = json.loads(data.decode("utf-8"))
            if "state" in payload:
                self.update_ui(payload["state"])
                
        except Exception as e:
            print(f"IPC Error: {e}")
            
        client.close()
        return False # Remove this client watch

    def play_sound(self, sound: Path):
        if self.settings.get("play_sounds", True):
            subprocess.Popen(
                ["paplay", str(sound)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    def show_notification(self, summary, icon):
        if self.settings.get("show_notifications", True):
            notification = Notify.Notification.new(summary, "", icon)
            # Make it transient so it doesn't stay in history
            notification.set_hint("transient", GLib.Variant.new_boolean(True))
            notification.show()

    def update_ui(self, state):
        self.state = state

        if state == "idle":
            self.indicator.set_icon_full(
                "audio-input-microphone-symbolic",
                "Idle"
            )

        elif state == "listening":
            self.indicator.set_icon_full(
                "media-record-symbolic",
                "Listening"
            )
            self.play_sound(START_SOUND)
            self.show_notification("🎙️ WayType: Listening...", "media-record-symbolic")

        elif state == "processing":
            self.indicator.set_icon_full(
                "media-playback-start-symbolic",
                "Processing"
            )

        elif state == "pasting":
            self.indicator.set_icon_full(
                "edit-paste-symbolic",
                "Pasting"
            )
            self.play_sound(COMPLETE_SOUND)
            self.show_notification("✅ WayType: Pasting Complete", "edit-paste-symbolic")

    def run(self):
        Gtk.main()

if __name__ == "__main__":
    app = VoiceTypingDaemon()
    try:
        app.run()
    except KeyboardInterrupt:
        Gtk.main_quit()
    finally:
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)
