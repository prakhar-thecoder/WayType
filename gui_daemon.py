import os
import json
import socket
import sys

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AyatanaAppIndicator3', '0.1')
from gi.repository import Gtk, GLib, AyatanaAppIndicator3 as AppIndicator

SOCKET_PATH = "/tmp/voice_typing_gui.sock"

class VoiceTypingDaemon:
    def __init__(self):
        self.state = "idle"
        
        # Setup AppIndicator
        self.indicator = AppIndicator.Indicator.new(
            "voice-typing-daemon",
            "audio-input-microphone-symbolic",
            AppIndicator.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self.menu = Gtk.Menu()
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

    def update_ui(self, state):
        self.state = state
        
        if state == "idle":
            self.indicator.set_icon_full("audio-input-microphone-symbolic", "Idle")
        else:
            if state == "listening":
                self.indicator.set_icon_full("media-record-symbolic", "Listening")
            elif state == "processing":
                self.indicator.set_icon_full("media-playback-start-symbolic", "Processing")
            elif state == "pasting":
                self.indicator.set_icon_full("edit-paste-symbolic", "Pasting")

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
