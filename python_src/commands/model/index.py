from __future__ import annotations

import os
from typing import Any

from deepseek_code.config import DeepSeekConfig
from python_src.utils.settings.applySettingsChange import applySettingsChange
from python_src.utils.settings.settings import getInitialSettings


async def model_command(
    action: str = "current",
    *,
    model: str | None = None,
    cwd: str | os.PathLike[str] | None = None,
) -> dict[str, Any]:
    config = DeepSeekConfig.from_env()
    settings = await getInitialSettings(cwd)
    models = list(config.models)
    current = model or settings.get("model") or settings.get("defaultModel") or config.default_model
    if action == "current":
        return {"model": current, "available_models": models, "default_model": config.default_model}
    if action == "list":
        return {"models": models, "default_model": config.default_model}
    if action == "set":
        if not model:
            raise ValueError("model is required for model set")
        updated = await applySettingsChange("model", model, cwd=cwd)
        return {"model": model, "settings": updated["settings"]}
    raise ValueError(f"Unsupported model action: {action}")


call = model_command
