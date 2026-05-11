from __future__ import annotations


MODEL_ALIASES = {
    "chat": "deepseek-chat",
    "coder": "deepseek-coder",
    "code": "deepseek-coder",
    "reasoner": "deepseek-reasoner",
    "deepseek-v3": "deepseek-chat",
    "deepseek-chat-v3": "deepseek-chat",
    "deepseek-r1": "deepseek-reasoner",
    # Claude compatibility aliases are intentionally mapped away from Anthropic.
    "sonnet": "deepseek-chat",
    "haiku": "deepseek-chat",
    "opus": "deepseek-reasoner",
}
MODEL_FAMILY_ALIASES = {
    "fast": "deepseek-chat",
    "balanced": "deepseek-chat",
    "coding": "deepseek-coder",
    "reasoning": "deepseek-reasoner",
}


async def isModelAlias(model: str) -> bool:
    return model in MODEL_ALIASES


async def isModelFamilyAlias(model: str) -> bool:
    return model in MODEL_FAMILY_ALIASES


def resolve_model_alias(model: str | None) -> str:
    if not model:
        return "deepseek-chat"
    normalized = model.strip()
    return MODEL_ALIASES.get(normalized, MODEL_FAMILY_ALIASES.get(normalized, normalized))
