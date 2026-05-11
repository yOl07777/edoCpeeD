from __future__ import annotations

from python_src.utils.model.configs import ALL_MODEL_CONFIGS


async def getModelOptions() -> list[dict[str, str]]:
    return [{"label": cfg["display_name"], "value": model} for model, cfg in ALL_MODEL_CONFIGS.items()]


async def getDefaultOptionForUser() -> dict[str, str]:
    return {"label": ALL_MODEL_CONFIGS["deepseek-chat"]["display_name"], "value": "deepseek-chat"}


async def getSonnet46_1MOption() -> dict[str, str]:
    return {"label": "DeepSeek Chat", "value": "deepseek-chat"}


async def getMaxSonnet46_1MOption() -> dict[str, str]:
    return await getSonnet46_1MOption()


async def getOpus46_1MOption() -> dict[str, str]:
    return {"label": "DeepSeek Reasoner", "value": "deepseek-reasoner"}


async def getMaxOpus46_1MOption() -> dict[str, str]:
    return await getOpus46_1MOption()
