from __future__ import annotations

import os
from typing import Any


MODE_PREFIXES = {
    "!": "shell",
    "/": "command",
    "@": "file",
    "#": "memory",
    "?": "help",
}


def prompt_payload(component: str, **kwargs: Any) -> dict[str, Any]:
    payload = {"type": component, "provider": "deepseek"}
    payload.update(kwargs)
    return payload


def mode_from_text(text: str) -> str:
    return MODE_PREFIXES.get(text[:1], "prompt")


def strip_mode_prefix(text: str) -> str:
    return text[1:] if text[:1] in MODE_PREFIXES else text


def truncate_text(text: str, limit: int = 20000) -> dict[str, Any]:
    if len(text) <= limit:
        return {"text": text, "truncated": False, "originalLength": len(text)}
    return {"text": text[:limit], "truncated": True, "originalLength": len(text)}


def vim_enabled() -> bool:
    return os.environ.get("DEEPCODE_VIM_MODE", "").lower() in {"1", "true", "yes"}

