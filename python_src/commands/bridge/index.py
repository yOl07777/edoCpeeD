"""Command metadata for `/remote-control`."""

from __future__ import annotations

from python_src.bridge.bridgeEnabled import isBridgeEnabled

from .bridge import call

bridge = {
    "type": "local-jsx",
    "name": "remote-control",
    "aliases": ["rc"],
    "description": "Connect this terminal for remote-control sessions",
    "argumentHint": "[name]",
    "isEnabled": isBridgeEnabled,
    "isHidden": lambda: not isBridgeEnabled(),
    "progressMessage": "Connecting remote-control bridge",
    "userFacingName": lambda: "remote-control",
    "call": call,
}

default = bridge
