"""Command metadata for `/stats`."""

from __future__ import annotations

from .stats import call, formatStats, getStats


stats = {
    "type": "local-jsx",
    "name": "stats",
    "description": "Show local session statistics",
    "supportsNonInteractive": True,
    "call": call,
}

default = stats

__all__ = ["call", "default", "formatStats", "getStats", "stats"]
