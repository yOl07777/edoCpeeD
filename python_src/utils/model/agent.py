from __future__ import annotations

from python_src.utils.model.modelOptions import getModelOptions
from python_src.utils.model.model import getMarketingNameForModel, normalizeModelStringForAPI


AGENT_MODEL_OPTIONS = [
    {"label": "DeepSeek Chat", "value": "deepseek-chat"},
    {"label": "DeepSeek Coder", "value": "deepseek-coder"},
    {"label": "DeepSeek Reasoner", "value": "deepseek-reasoner"},
]


async def getDefaultSubagentModel() -> str:
    return "deepseek-chat"


async def getAgentModel(model: str | None = None) -> str:
    return await normalizeModelStringForAPI(model or await getDefaultSubagentModel())


async def getAgentModelDisplay(model: str | None = None) -> str:
    return await getMarketingNameForModel(await getAgentModel(model))


async def getAgentModelOptions() -> list[dict[str, str]]:
    return await getModelOptions()
