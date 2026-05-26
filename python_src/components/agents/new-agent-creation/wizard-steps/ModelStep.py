from __future__ import annotations

from typing import Any

from python_src.components.agents.ModelSelector import ModelSelector
from python_src.components.agents._shared import component_result


async def ModelStep(*args: Any, **kwargs: Any) -> Any:
    selected = kwargs.get("model") or kwargs.get("selected") or (args[0] if args else "deepseek-chat")
    return component_result("agent_wizard_model_step", field="model", selector=await ModelSelector(selected), complete=True)


__all__ = ["ModelStep"]
