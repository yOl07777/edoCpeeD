"""Command metadata for `/fast`."""

from __future__ import annotations

from python_src.utils.fastMode import FAST_MODE_MODEL_DISPLAY, isFastModeEnabled

from .fast import call

fast = {
    "type": "local-jsx",
    "name": "fast",
    "description": lambda: f"Toggle fast mode ({FAST_MODE_MODEL_DISPLAY} only)",
    "availability": ["deepseek", "console"],
    "isEnabled": isFastModeEnabled,
    "isHidden": lambda: not isFastModeEnabled(),
    "argumentHint": "[on|off]",
    "immediate": True,
    "call": call,
}

default = fast
