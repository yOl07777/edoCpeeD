from __future__ import annotations

from typing import Any

from ._basic import first_mapping, pick


async def useTeleportResume(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    token = pick(options, "token", "resumeToken", default=None)
    repo = pick(options, "repo", "repository", default=None)
    return {
        "provider": "deepseek",
        "canResume": bool(token),
        "resumeToken": token,
        "repo": repo,
        "prompt": f"Resume DeepSeek Teleport session for {repo}." if token else "",
    }
