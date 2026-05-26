"""Command metadata for `/rewind`."""

from __future__ import annotations

from .rewind import call


rewind = {
    "type": "local",
    "name": "rewind",
    "description": "Rewind the last in-memory session message",
    "supportsNonInteractive": True,
    "call": call,
}

default = rewind

__all__ = ["call", "default", "rewind"]
