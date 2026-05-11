from __future__ import annotations

import asyncio
import os
import re
from typing import Any

from python_src.utils.git.gitFilesystem import getCachedBranch, getCachedDefaultBranch


def _slug(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return re.sub(r"-{2,}", "-", slug)[:60] or "work"


async def deriveFirstPrompt(prompt: str, *, prefix: str = "deepseek") -> str:
    return f"{prefix}/{_slug(prompt)}"


async def _run_git(*args: str, cwd: str | None = None) -> dict[str, Any]:
    try:
        proc = await asyncio.create_subprocess_exec(
            "git",
            *args,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=15)
    except FileNotFoundError:
        return {"exit_code": 127, "stdout": "", "stderr": "git is not installed"}
    except asyncio.TimeoutError:
        return {"exit_code": 124, "stdout": "", "stderr": "git command timed out"}
    return {
        "exit_code": proc.returncode,
        "stdout": stdout.decode(errors="replace"),
        "stderr": stderr.decode(errors="replace"),
    }


async def call(
    action: str = "current",
    *,
    name: str | None = None,
    prompt: str | None = None,
    cwd: str | os.PathLike[str] | None = None,
    create: bool = False,
) -> dict[str, Any]:
    cwd_str = str(cwd) if cwd else None
    if action == "current":
        return {"branch": await getCachedBranch(cwd_str), "default_branch": await getCachedDefaultBranch(cwd_str)}
    if action == "derive":
        if not prompt:
            raise ValueError("prompt is required for branch derive")
        return {"branch": await deriveFirstPrompt(prompt)}
    if action == "list":
        result = await _run_git("branch", "--format=%(refname:short)", cwd=cwd_str)
        branches = [line.strip() for line in result["stdout"].splitlines() if line.strip()]
        return {**result, "branches": branches}
    if action in {"create", "checkout"}:
        branch = name or (await deriveFirstPrompt(prompt or "work"))
        args = ["checkout", "-b", branch] if create or action == "create" else ["checkout", branch]
        result = await _run_git(*args, cwd=cwd_str)
        return {**result, "branch": branch}
    raise ValueError(f"Unsupported branch action: {action}")
