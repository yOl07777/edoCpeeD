from __future__ import annotations

from typing import Any


DEFAULT_TIPS = [
    {"id": "stream", "text": "使用 --stream 可以实时查看 DeepSeek 输出。", "tags": ["cli", "deepseek"]},
    {"id": "tools", "text": "使用 --enable-tools 可启用本地文件、搜索和 shell 工具。", "tags": ["tools"]},
    {"id": "permissions", "text": "命令工具会先经过本地权限和危险命令校验。", "tags": ["security", "tools"]},
    {"id": "model", "text": "可通过 --model 或 /model set 切换 DeepSeek 模型。", "tags": ["model"]},
]


async def getRelevantTips(context: dict[str, Any] | None = None, *, tags: list[str] | None = None) -> list[dict[str, Any]]:
    wanted = set(tags or (context or {}).get("tags") or [])
    if not wanted:
        return list(DEFAULT_TIPS)
    return [tip for tip in DEFAULT_TIPS if wanted.intersection(tip.get("tags", []))]
