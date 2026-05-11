from __future__ import annotations

from python_src.utils.model.aliases import resolve_model_alias
from python_src.utils.model.configs import ALL_MODEL_CONFIGS


_INITIALIZED = False


async def ensureModelStringsInitialized() -> bool:
    global _INITIALIZED
    _INITIALIZED = True
    return _INITIALIZED


async def getModelStrings() -> dict[str, str]:
    await ensureModelStringsInitialized()
    return {key: value["display_name"] for key, value in ALL_MODEL_CONFIGS.items()}


async def resolveOverriddenModel(model: str | None, override: str | None = None) -> str:
    return resolve_model_alias(override or model)
