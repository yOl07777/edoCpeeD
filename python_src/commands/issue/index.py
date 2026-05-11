from __future__ import annotations

import json
import os
from typing import Any

from python_src.utils.github.ghAuthStatus import _run_gh


async def issue_command(
    action: str = "list",
    *,
    number: int | None = None,
    state: str = "open",
    limit: int = 20,
    cwd: str | os.PathLike[str] | None = None,
) -> dict[str, Any]:
    cwd_str = str(cwd) if cwd else None
    if action == "view":
        if number is None:
            raise ValueError("number is required for issue view")
        result = await _run_gh(
            "issue",
            "view",
            str(number),
            "--json",
            "number,title,state,body,author,url,labels,comments",
            cwd=cwd_str,
        )
    elif action == "list":
        result = await _run_gh(
            "issue",
            "list",
            "--state",
            state,
            "--limit",
            str(limit),
            "--json",
            "number,title,state,author,url,labels",
            cwd=cwd_str,
        )
    else:
        raise ValueError(f"Unsupported issue action: {action}")
    parsed = None
    if result["stdout"].strip():
        try:
            parsed = json.loads(result["stdout"])
        except json.JSONDecodeError:
            parsed = None
    return {**result, "action": action, "data": parsed}


call = issue_command
