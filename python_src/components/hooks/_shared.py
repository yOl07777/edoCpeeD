from __future__ import annotations

from typing import Any


HOOK_EVENTS = ["PreToolUse", "PostToolUse", "Notification", "Stop", "SubagentStop"]
HOOK_MODES = ["view", "add", "edit", "remove"]
MATCHER_MODES = ["all", "tool", "command", "regex"]


def hook_payload(component: str, **kwargs: Any) -> dict[str, Any]:
    payload = {"type": component, "provider": "deepseek"}
    payload.update(kwargs)
    return payload


def normalize_hook(hook: Any = None, **kwargs: Any) -> dict[str, Any]:
    data = dict(hook) if isinstance(hook, dict) else {}
    data.update({key: value for key, value in kwargs.items() if value is not None})
    event = data.get("event") or data.get("hookEvent") or "PreToolUse"
    command = data.get("command") or data.get("prompt") or ""
    matcher = data.get("matcher") or data.get("pattern") or "*"
    return {
        "event": str(event),
        "matcher": str(matcher),
        "command": str(command),
        "enabled": bool(data.get("enabled", True)),
        "source": str(data.get("source") or "project"),
    }

