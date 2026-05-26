from __future__ import annotations

from typing import Any

from python_src.components.agents._shared import component_result


async def AgentNavigationFooter(*args: Any, **kwargs: Any) -> Any:
    mode = kwargs.get("mode") or (args[0] if args else "main-menu")
    return component_result(
        "agent_navigation_footer",
        mode=str(mode),
        shortcuts=[
            {"key": "enter", "label": "select"},
            {"key": "esc", "label": "back"},
            {"key": "q", "label": "close"},
        ],
    )


__all__ = ["AgentNavigationFooter"]
