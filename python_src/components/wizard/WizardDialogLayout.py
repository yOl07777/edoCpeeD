from __future__ import annotations

from typing import Any

from python_src.components.wizard._shared import wizard_payload


async def WizardDialogLayout(*args: Any, **kwargs: Any) -> Any:
    return wizard_payload("wizard_dialog_layout", title=str(kwargs.get("title") or "Wizard"), body=kwargs.get("body") or (args[0] if args else None), footer=kwargs.get("footer"))


__all__ = ["WizardDialogLayout"]
