"""
main.py — WayType entry point.

Activates .env loading and delegates to the core pipeline.
"""

import config  # noqa: F401 — ensures .env is loaded before any other import
from core.pipeline import run

if __name__ == "__main__":
    raise SystemExit(run())