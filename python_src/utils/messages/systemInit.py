from __future__ import annotations

import platform
from typing import Any


def sdkCompatToolName(name: str) -> str:
    return name.replace("-", "_").replace(" ", "_")


async def buildSystemInitMessage(
    *,
    model: str = "deepseek-chat",
    cwd: str | None = None,
    tools: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    tool_names = []
    for tool in tools or []:
        if "function" in tool:
            tool_names.append(tool["function"].get("name"))
        else:
            tool_names.append(tool.get("name"))
    content = [
        "DeepSeek Code Python runtime initialized.",
        f"Model: {model}",
        f"Platform: {platform.system()} {platform.release()}",
    ]
    if cwd:
        content.append(f"Working directory: {cwd}")
    if tool_names:
        content.append("Tools: " + ", ".join(filter(None, map(str, tool_names))))
    return {"role": "system", "content": "\n".join(content)}
