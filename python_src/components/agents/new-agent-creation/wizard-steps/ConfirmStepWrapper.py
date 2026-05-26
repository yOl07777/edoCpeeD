from __future__ import annotations

from typing import Any

from python_src.components.agents._shared import component_result


async def ConfirmStepWrapper(*args: Any, **kwargs: Any) -> Any:
    return component_result("agent_wizard_confirm_wrapper", title="Review agent", content=kwargs.get("content") or (args[0] if args else None))


__all__ = ["ConfirmStepWrapper"]
