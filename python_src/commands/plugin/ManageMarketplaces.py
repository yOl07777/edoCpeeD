from __future__ import annotations

from typing import Any

from python_src.commands.plugin._shared import command_result, list_marketplaces


async def ManageMarketplaces(*args: Any, **kwargs: Any) -> dict[str, Any]:
    marketplaces = await list_marketplaces()
    return command_result(
        f"Configured marketplaces: {len(marketplaces['items'])}.",
        marketplaces=marketplaces["items"],
        path=marketplaces.get("path"),
    )


__all__ = ["ManageMarketplaces"]
