from __future__ import annotations

from .copy import call

copy = {
    "type": "local-jsx",
    "name": "copy",
    "description": "Copy DeepSeek Code's last response to a temp file",
    "call": call,
}

default = copy
