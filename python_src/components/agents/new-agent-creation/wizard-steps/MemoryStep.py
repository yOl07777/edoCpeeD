from __future__ import annotations

from typing import Any

from python_src.components.agents._shared import component_result


async def MemoryStep(*args: Any, **kwargs: Any) -> Any:
    value = kwargs.get("memory") if "memory" in kwargs else (args[0] if args else None)
    return component_result("agent_wizard_memory_step", field="memory", value=value, enabled=bool(value), complete=True)


__all__ = ["MemoryStep"]
