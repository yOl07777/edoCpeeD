from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, scalar_arg


async def ThinkingToggle(*args: Any, **kwargs: Any) -> dict[str, Any]:
    enabled = bool(option(args, kwargs, "enabled", scalar_arg(args, False)))
    model = str(option(args, kwargs, "model", "deepseek-reasoner") or "deepseek-reasoner")
    return component_payload("thinking_toggle", enabled=enabled, model=model, label="Reasoning" if enabled else "Fast")


__all__ = ["ThinkingToggle"]
