"""Command metadata for `/btw`."""

from __future__ import annotations

from .btw import call

btw = {
    "type": "local-jsx",
    "name": "btw",
    "description": "Ask a quick side question without interrupting the main conversation",
    "isEnabled": lambda: True,
    "isHidden": lambda: False,
    "argumentHint": "<question>",
    "progressMessage": "Asking side question",
    "userFacingName": lambda: "btw",
    "call": call,
}

default = btw
