from __future__ import annotations

import os
from typing import Any

from deepseek_code.config import DeepSeekConfig
from python_src.utils.model.aliases import resolve_model_alias
from python_src.utils.model.configs import ALL_MODEL_CONFIGS


async def normalizeModelStringForAPI(model: str | None) -> str:
    return resolve_model_alias(model or DeepSeekConfig.from_env().default_model)


async def getCanonicalName(model: str | None) -> str:
    return await normalizeModelStringForAPI(model)


async def firstPartyNameToCanonical(model: str | None) -> str:
    return await normalizeModelStringForAPI(model)


async def getDefaultMainLoopModel() -> str:
    return DeepSeekConfig.from_env().default_model


async def getDefaultMainLoopModelSetting() -> str:
    return await getDefaultMainLoopModel()


async def getMainLoopModel(model: str | None = None) -> str:
    return await normalizeModelStringForAPI(model)


async def getRuntimeMainLoopModel(model: str | None = None) -> str:
    return await getMainLoopModel(model)


async def getSmallFastModel() -> str:
    return "deepseek-chat"


async def getDefaultHaikuModel() -> str:
    return "deepseek-chat"


async def getDefaultSonnetModel() -> str:
    return "deepseek-chat"


async def getDefaultOpusModel() -> str:
    return "deepseek-reasoner"


async def getBestModel(task: str | None = None) -> str:
    text = (task or "").lower()
    if "code" in text or "coding" in text or "program" in text:
        return "deepseek-coder"
    if "reason" in text or "math" in text or "plan" in text:
        return "deepseek-reasoner"
    return await getDefaultMainLoopModel()


async def getMarketingNameForModel(model: str | None) -> str:
    canonical = await normalizeModelStringForAPI(model)
    return ALL_MODEL_CONFIGS.get(canonical, {}).get("display_name", canonical)


async def getPublicModelDisplayName(model: str | None) -> str:
    return await getMarketingNameForModel(model)


async def getPublicModelName(model: str | None) -> str:
    return await normalizeModelStringForAPI(model)


async def renderModelName(model: str | None) -> str:
    return await getPublicModelDisplayName(model)


async def modelDisplayString(model: str | None) -> str:
    return await renderModelName(model)


async def renderModelSetting(model: str | None) -> str:
    return await normalizeModelStringForAPI(model)


async def renderDefaultModelSetting() -> str:
    return await getDefaultMainLoopModel()


async def parseUserSpecifiedModel(model: str | None) -> str | None:
    return await normalizeModelStringForAPI(model) if model else None


async def getUserSpecifiedModelSetting(model: str | None = None) -> str | None:
    return await parseUserSpecifiedModel(model or os.getenv("DEFAULT_MODEL"))


async def getClaudeAiUserDefaultModelDescription() -> str:
    return "DeepSeek default model"


async def getOpus46PricingSuffix() -> str:
    return ""


async def isLegacyModelRemapEnabled() -> bool:
    return True


async def isOpus1mMergeEnabled() -> bool:
    return False


async def isNonCustomOpusModel(model: str | None) -> bool:
    return await normalizeModelStringForAPI(model) == "deepseek-reasoner"


async def resolveSkillModelOverride(skill: dict[str, Any] | None = None, fallback: str | None = None) -> str:
    if isinstance(skill, dict):
        override = skill.get("model") or skill.get("default_model")
        if override:
            return await normalizeModelStringForAPI(str(override))
    return await normalizeModelStringForAPI(fallback)
