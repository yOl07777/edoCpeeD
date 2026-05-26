"""Command metadata for `/resume`."""

from __future__ import annotations

from .resume import call, filterResumableSessions, formatResumableSessions


resume = {
    "type": "local-jsx",
    "name": "resume",
    "description": "List resumable local sessions",
    "supportsNonInteractive": True,
    "call": call,
}

default = resume

__all__ = ["call", "default", "filterResumableSessions", "formatResumableSessions", "resume"]
