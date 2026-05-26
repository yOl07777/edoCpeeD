from __future__ import annotations

from .effort import call

effort = {
    "type": "local-jsx",
    "name": "effort",
    "description": "Set effort level for model usage",
    "argumentHint": "[low|medium|high|max|auto]",
    "call": call,
}

default = effort
