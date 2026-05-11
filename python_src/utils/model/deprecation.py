from __future__ import annotations


async def getModelDeprecationWarning(model: str | None) -> str | None:
    if model and "claude" in model.lower():
        return "Claude model names are remapped in this Python migration; use a DeepSeek model such as deepseek-chat."
    return None
