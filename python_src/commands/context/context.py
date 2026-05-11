from __future__ import annotations

from typing import Any

import importlib


async def call(messages: list[dict[str, Any]] | None = None, **kwargs: Any) -> dict[str, Any]:
    module = importlib.import_module("python_src.commands.context.context-noninteractive")
    return await module.collectContextData(messages, **kwargs)
