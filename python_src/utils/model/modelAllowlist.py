from __future__ import annotations

from python_src.utils.model.validateModel import validateModel


async def isModelAllowed(model: str | None) -> bool:
    return bool((await validateModel(model))["ok"])
