"""Command metadata for `/session`."""

from __future__ import annotations

from .session import call, session_command


session = {
    "type": "local",
    "name": "session",
    "description": "Manage the lightweight in-process conversation session",
    "supportsNonInteractive": True,
    "call": call,
}

session_command_metadata = session
default = session

__all__ = ["call", "default", "session", "session_command", "session_command_metadata"]
