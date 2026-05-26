"""Command metadata for `/feedback`."""

from __future__ import annotations

import os

from .feedback import call


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def isEnabled() -> bool:
    disabled = any(
        _truthy(os.getenv(name))
        for name in (
            "CLAUDE_CODE_USE_BEDROCK",
            "CLAUDE_CODE_USE_VERTEX",
            "CLAUDE_CODE_USE_FOUNDRY",
            "DISABLE_FEEDBACK_COMMAND",
            "DISABLE_BUG_COMMAND",
        )
    )
    return not disabled and os.getenv("USER_TYPE") != "ant"


feedback = {
    "aliases": ["bug"],
    "type": "local-jsx",
    "name": "feedback",
    "description": "Submit feedback about DeepSeek Code",
    "argumentHint": "[report]",
    "isEnabled": isEnabled,
    "call": call,
}

default = feedback
