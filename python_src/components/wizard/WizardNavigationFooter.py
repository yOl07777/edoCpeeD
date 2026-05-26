from __future__ import annotations

from typing import Any

from python_src.components.wizard._shared import wizard_payload


async def WizardNavigationFooter(*args: Any, **kwargs: Any) -> Any:
    current = int(kwargs.get("current", args[0] if args else 0) or 0)
    total = int(kwargs.get("total", args[1] if len(args) > 1 else 1) or 1)
    return wizard_payload("wizard_navigation_footer", current=current, total=total, actions=["back", "next", "cancel", "finish"], canFinish=current >= total - 1)


__all__ = ["WizardNavigationFooter"]
