from __future__ import annotations

from typing import Any

from python_src.components.CustomSelect._shared import normalize_options


async def createOptionMap(options: Any = None, *_args: Any, **_kwargs: Any) -> dict[Any, dict[str, Any]]:
    return {option["value"]: option for option in normalize_options(options or [])}


optionMap = createOptionMap


__all__ = ["createOptionMap", "optionMap"]
