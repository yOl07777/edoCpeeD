from __future__ import annotations

from typing import Any

from python_src.components.agents._shared import component_result


async def AgentsMenu(*args: Any, **kwargs: Any) -> Any:
    selected = int(kwargs.get("selected", 0) or 0)
    items = [
        {"id": "list-agents", "label": "List agents"},
        {"id": "create-agent", "label": "Create agent"},
        {"id": "edit-agent", "label": "Edit agent"},
        {"id": "delete-agent", "label": "Delete agent"},
    ]
    return component_result("agents_menu", items=items, selected=max(0, min(selected, len(items) - 1)))


__all__ = ["AgentsMenu"]
