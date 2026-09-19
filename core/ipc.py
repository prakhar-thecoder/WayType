"""
core/ipc.py

Shared Unix-socket IPC utilities.

Protocol constants and the client-side `notify_gui` function live here so
that core/pipeline.py does not need to depend on anything in ui/.

The server side (socket setup, GLib watch, message dispatch) lives in
ui/daemon.py.
"""

import json
import socket

SOCKET_PATH = "/tmp/waytype_gui.sock"

# Valid state names understood by the GUI daemon.
STATE_IDLE = "idle"
STATE_LISTENING = "listening"
STATE_PROCESSING = "processing"
STATE_PASTING = "pasting"


def notify_gui(state: str) -> None:
    """Send a state update to the GUI daemon over the Unix domain socket.

    Silently no-ops if the daemon is not running.
    """
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(SOCKET_PATH)
        sock.sendall(json.dumps({"state": state}).encode("utf-8"))
        sock.close()
    except Exception:
        pass
