from __future__ import annotations

from typing import Any

from python_src.utils.model.aliases import resolve_model_alias
from python_src.utils.model.configs import ALL_MODEL_CONFIGS


_CAPABILITIES = {key: dict(value) for key, value in ALL_MODEL_CONFIGS.items()}


async def refreshModelCapabilities(overrides: dict[str, dict[str, Any]] | None = None) -> dict[str, dict[str, Any]]:
    if overrides:
        for model, values in overrides.items():
            canonical = resolve_model_alias(model)
            _CAPABILITIES.setdefault(canonical, {}).update(values)
    return {key: dict(value) for key, value in _CAPABILITIES.items()}


async def getModelCapability(model: str, capability: str | None = None) -> Any:
    canonical = resolve_model_alias(model)
    data = _CAPABILITIES.get(canonical, {"id": canonical, "supports_streaming": True})
    return data.get(capability) if capability else dict(data)
