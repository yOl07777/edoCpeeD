from __future__ import annotations

from deepseek_code.config import DeepSeekConfig
from python_src.utils.model.aliases import resolve_model_alias


async def validateModel(model: str | None) -> dict[str, object]:
    canonical = resolve_model_alias(model)
    allowed = set(DeepSeekConfig.from_env().models) | {"deepseek-chat", "deepseek-coder", "deepseek-reasoner"}
    ok = canonical in allowed or canonical.startswith("deepseek-")
    return {
        "ok": ok,
        "model": canonical,
        "reason": None if ok else f"Model {model!r} is not configured for DeepSeek.",
    }
