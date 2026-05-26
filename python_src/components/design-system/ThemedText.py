from __future__ import annotations

from typing import Any

from importlib import import_module


TextHoverColorContext: dict[str, Any] = {"provider": "deepseek", "hoverColor": "accent"}


async def ThemedText(*args: Any, **kwargs: Any) -> Any:
    shared = import_module("python_src.components.design-system._shared")
    variant = kwargs.get("variant", "body")
    return shared.ui_payload("themed_text", text=str(kwargs.get("text") or (args[0] if args else "")), variant=variant, color=kwargs.get("color", "foreground"))


__all__ = ["TextHoverColorContext", "ThemedText"]
