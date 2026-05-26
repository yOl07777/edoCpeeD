from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg


async def LogSelector(*args: Any, **kwargs: Any) -> Any:
    selected = str(option(args, kwargs, "selected", scalar_arg(args, "")))
    logs = normalize_items(option(args, kwargs, "logs", []), text_key="path")
    for log in logs:
        log["selected"] = log["path"] == selected
    return component_payload("log_selector", selected=selected, logs=logs, count=len(logs))


__all__ = ["LogSelector"]
