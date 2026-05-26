from __future__ import annotations

from .color import call

color = {
    "type": "local-jsx",
    "name": "color",
    "description": "Set the prompt bar color for this session",
    "immediate": True,
    "argumentHint": "<color|default>",
    "call": call,
}

default = color
