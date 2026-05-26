from __future__ import annotations

from typing import Any


def settings_payload(component: str, **kwargs: Any) -> dict[str, Any]:
    payload = {"type": component, "provider": "deepseek"}
    payload.update(kwargs)
    return payload


def safe_config(config: Any) -> dict[str, Any]:
    if not isinstance(config, dict):
        return {}
    cleaned: dict[str, Any] = {}
    for key, value in config.items():
        lowered = str(key).lower()
        cleaned[key] = "***" if any(token in lowered for token in ["key", "token", "secret", "password"]) else value
    return cleaned

