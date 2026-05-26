from __future__ import annotations

from typing import Any

from ._notification import first_mapping, pick


async def useSettingsErrors(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    errors = pick(options, "errors", default=[]) or []
    if isinstance(errors, str):
        errors = [errors]
    return {
        "provider": "deepseek",
        "visible": bool(errors),
        "level": "error" if errors else "info",
        "title": "Settings errors",
        "errors": list(errors),
        "message": "; ".join(str(error) for error in errors),
    }
