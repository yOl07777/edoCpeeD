from __future__ import annotations

import os
from typing import Any

from python_src.commands.diff.index import diff_command
from python_src.commands.review.ultrareviewEnabled import isUltrareviewEnabled


async def checkOverageGate(diff_text: str, *, max_chars: int = 80_000) -> dict[str, Any]:
    over = len(diff_text) > max_chars
    return {"allowed": not over, "overage": over, "size": len(diff_text), "max_chars": max_chars}


async def confirmOverage(*, assume_yes: bool = False) -> bool:
    return bool(assume_yes)


async def launchRemoteReview(
    *,
    cwd: str | os.PathLike[str] | None = None,
    staged: bool = False,
    assume_yes: bool = False,
    max_chars: int = 80_000,
) -> dict[str, Any]:
    if not await isUltrareviewEnabled():
        return {"started": False, "reason": "Review is disabled by DEEPSEEK_REVIEW_ENABLED."}
    diff = await diff_command(cwd=cwd, staged=staged, max_chars=max_chars + 1)
    gate = await checkOverageGate(diff["stdout"], max_chars=max_chars)
    if not gate["allowed"] and not await confirmOverage(assume_yes=assume_yes):
        return {"started": False, "reason": "Diff exceeds review size limit.", "gate": gate}
    prompt = (
        "请审查以下 git diff，优先指出 bug、行为回归、安全风险和缺失测试。\n\n"
        f"{diff['stdout'][:max_chars]}"
    )
    return {
        "started": True,
        "mode": "local_prompt",
        "files": diff["files"],
        "gate": gate,
        "prompt": prompt,
    }
