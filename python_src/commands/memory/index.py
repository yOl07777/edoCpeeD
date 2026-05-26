"""Command metadata for `/memory`."""

from __future__ import annotations

from .memory import call, memory_command


memory = {
    "type": "local",
    "name": "memory",
    "description": "Read, append, or render local project memory",
    "supportsNonInteractive": True,
    "call": call,
}

memory_command_metadata = memory
default = memory

__all__ = ["call", "default", "memory", "memory_command", "memory_command_metadata"]
