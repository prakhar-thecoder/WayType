"""
core/context.py

Minimal placeholder for future runtime context.

This module is NOT used in the current application pipeline.
It is reserved for a future feature (e.g., Intelligent Typing) that may
need lightweight contextual data such as user name, current date/time, or
timezone at inference time.

Do NOT integrate this into the current normal formatter.
Do NOT add memory, database, contacts, or agent systems here.
"""

from datetime import datetime, timezone
from typing import Any


def get_runtime_context() -> dict[str, Any]:
    """Return a minimal snapshot of the current runtime context.

    Currently unused. Reserved for future Intelligent Typing feature.
    """
    now = datetime.now(tz=timezone.utc).astimezone()
    return {
        "current_datetime": now.isoformat(),
        "timezone": str(now.tzinfo),
    }
