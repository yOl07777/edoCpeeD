"""Command metadata for `/voice`."""

from __future__ import annotations

from .voice import call


voice = {
    "type": "local",
    "name": "voice",
    "description": "Toggle voice mode",
    "supportsNonInteractive": True,
    "call": call,
}

default = voice

__all__ = ["call", "default", "voice"]
