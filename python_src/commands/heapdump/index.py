"""Command metadata for `/heapdump`."""

from __future__ import annotations

from .heapdump import call

heapDump = {
    "type": "local",
    "name": "heapdump",
    "description": "Dump Python runtime diagnostics to the desktop",
    "isHidden": True,
    "supportsNonInteractive": True,
    "call": call,
}

default = heapDump
