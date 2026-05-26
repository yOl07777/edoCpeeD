from __future__ import annotations

from typing import Any


def useInput(*args: Any, **kwargs: Any) -> dict[str, Any]:
    handler = args[0] if args else kwargs.get("handler")
    enabled = bool(kwargs.get("enabled", True))
    events: list[dict[str, Any]] = []

    def dispatch(value: str, key: dict[str, Any] | None = None) -> Any:
        event = {"input": value, "key": key or {}}
        events.append(event)
        if enabled and callable(handler):
            return handler(value, key or {})
        return None

    return {"provider": "deepseek", "enabled": enabled, "events": events, "dispatch": dispatch}


default = useInput
_module_migration_placeholder = useInput
