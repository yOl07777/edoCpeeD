from __future__ import annotations

from typing import Any

from python_src.components.wizard.useWizard import useWizard


WizardContext: dict[str, Any] = {"provider": "deepseek", "steps": [], "currentIndex": 0}


async def WizardProvider(*args: Any, **kwargs: Any) -> Any:
    state = await useWizard(kwargs.get("steps") or (args[0] if args else []), current=kwargs.get("current", 0))
    WizardContext.update(state)
    return state


__all__ = ["WizardContext", "WizardProvider"]
