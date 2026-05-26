from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg
from python_src.components.AutoUpdater import AutoUpdater


async def AutoUpdaterWrapper(*args: Any, **kwargs: Any) -> Any:
    updater = await AutoUpdater(*args, **kwargs)
    children = normalize_items(option(args, kwargs, "children", scalar_arg(args)))
    return component_payload("auto_updater_wrapper", updater=updater, children=children, enabled=bool(option(args, kwargs, "enabled", True)))


__all__ = ["AutoUpdaterWrapper"]
