"""Command metadata for `/agents`."""

from __future__ import annotations

from .agents import call

agents = {
    "type": "local-jsx",
    "name": "agents",
    "description": "Manage agent configurations",
    "call": call,
}

default = agents
