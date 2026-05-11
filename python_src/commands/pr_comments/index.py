from __future__ import annotations

import json
import os
from typing import Any

from python_src.utils.github.ghAuthStatus import _run_gh


async def pr_comments_command(
    number: int | None = None,
    *,
    cwd: str | os.PathLike[str] | None = None,
) -> dict[str, Any]:
    args = ["pr", "view"]
    if number is not None:
        args.append(str(number))
    args += ["--json", "number,title,url,comments,reviews"]
    result = await _run_gh(*args, cwd=str(cwd) if cwd else None)
    data = None
    if result["stdout"].strip():
        try:
            data = json.loads(result["stdout"])
        except json.JSONDecodeError:
            data = None
    comments = []
    if isinstance(data, dict):
        comments.extend(data.get("comments") or [])
        for review in data.get("reviews") or []:
            body = review.get("body")
            if body:
                comments.append(review)
    return {**result, "data": data, "comments": comments, "count": len(comments)}


call = pr_comments_command
