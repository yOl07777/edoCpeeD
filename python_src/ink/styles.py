from __future__ import annotations

from typing import Any


def normalizeStyles(*args: Any, **kwargs: Any) -> dict[str, Any]:
    style = dict(args[0] if args and isinstance(args[0], dict) else kwargs.get("style", {}) or {})
    for key in ("margin", "padding"):
        value = style.get(key)
        if isinstance(value, int):
            style[key] = {"top": value, "right": value, "bottom": value, "left": value}
    return style


default = normalizeStyles
_module_migration_placeholder = normalizeStyles
