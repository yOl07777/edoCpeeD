from __future__ import annotations

from typing import Any

from python_src.commands.plugin._shared import paginate


async def usePagination(items: list[Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    return paginate(
        list(items or kwargs.get("items") or []),
        page=int(kwargs.get("page", 1)),
        per_page=int(kwargs.get("perPage", kwargs.get("per_page", 10))),
    )


__all__ = ["usePagination"]
