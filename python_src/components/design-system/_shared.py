from __future__ import annotations

from typing import Any


THEMES = {
    "dark": {"background": "#111111", "foreground": "#f3f4f6", "accent": "#2dd4bf", "muted": "#9ca3af"},
    "light": {"background": "#ffffff", "foreground": "#111827", "accent": "#0f766e", "muted": "#6b7280"},
}


def ui_payload(component: str, **kwargs: Any) -> dict[str, Any]:
    payload = {"type": component, "provider": "deepseek"}
    payload.update(kwargs)
    return payload


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def theme(name: str | None = None) -> dict[str, str]:
    return THEMES.get(str(name or "dark"), THEMES["dark"])

