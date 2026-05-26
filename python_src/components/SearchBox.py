from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, scalar_arg


async def SearchBox(*args: Any, **kwargs: Any) -> Any:
    query = str(option(args, kwargs, "query", scalar_arg(args, "")))
    return component_payload("search_box", query=query, placeholder=str(option(args, kwargs, "placeholder", "Search")), active=bool(option(args, kwargs, "active", True)))


__all__ = ["SearchBox"]
