"""
core/settings.py

Single source of truth for user-facing WayType settings.

Handles:
  - settings file location (settings.json at the repository root)
  - default values
  - loading with safe fallback
  - saving
"""

import json
from pathlib import Path

# Repository root is the directory containing this package's parent (core/).
_REPO_ROOT = Path(__file__).resolve().parent.parent
SETTINGS_FILE = _REPO_ROOT / "settings.json"

DEFAULTS: dict = {
    "play_sounds": True,
    "show_notifications": True,
    "format_text": True,
    "listen_indefinitely": False,
    "silence_timeout": 1.0,
}


def load() -> dict:
    """Load settings from disk. Missing keys fall back to DEFAULTS."""
    settings = dict(DEFAULTS)
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r") as f:
                settings.update(json.load(f))
        except Exception as exc:
            print(f"[Settings] Failed to load settings, using defaults: {exc}", flush=True)
    return settings


def save(settings: dict) -> None:
    """Persist settings to disk."""
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f)
    except Exception as exc:
        print(f"[Settings] Failed to save settings: {exc}", flush=True)
