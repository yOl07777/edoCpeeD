from __future__ import annotations

from typing import Any

from python_src.components.agents._shared import AGENT_MODELS, component_result


async def ModelSelector(*args: Any, **kwargs: Any) -> Any:
    selected = str(kwargs.get("selected") or (args[0] if args else "") or "deepseek-chat")
    models = kwargs.get("models") or AGENT_MODELS
    return component_result(
        "model_selector",
        models=[{"id": model, "selected": model == selected} for model in models],
        selected=selected,
    )


__all__ = ["ModelSelector"]
