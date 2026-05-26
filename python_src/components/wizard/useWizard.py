from __future__ import annotations

from typing import Any

from python_src.components.wizard._shared import normalize_steps, wizard_payload


async def useWizard(*args: Any, **kwargs: Any) -> Any:
    steps = normalize_steps(kwargs.get("steps") or (args[0] if args else []))
    current = int(kwargs.get("current", kwargs.get("currentIndex", 0)) or 0)
    current = max(0, min(current, max(0, len(steps) - 1)))
    return wizard_payload("wizard_state", steps=steps, currentIndex=current, current=steps[current] if steps else None, canBack=current > 0, canNext=current < len(steps) - 1)


__all__ = ["useWizard"]
