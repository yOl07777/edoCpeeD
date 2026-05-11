from __future__ import annotations

import asyncio
import os
from typing import Any


async def diff_command(
    *,
    cwd: str | os.PathLike[str] | None = None,
    staged: bool = False,
    name_only: bool = False,
    max_chars: int = 50_000,
) -> dict[str, Any]:
    args = ["git", "diff"]
    if staged:
        args.append("--staged")
    if name_only:
        args.append("--name-only")
    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            cwd=str(cwd) if cwd else None,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=15)
    except (FileNotFoundError, asyncio.TimeoutError):
        return {"exit_code": 1, "stdout": "", "stderr": "git diff unavailable", "files": [], "truncated": False}

    text = stdout.decode(errors="replace")
    files = []
    for line in text.splitlines():
        if line.startswith("diff --git "):
            parts = line.split()
            if len(parts) >= 4:
                files.append(parts[3].removeprefix("b/"))
        elif name_only and line.strip():
            files.append(line.strip())
    return {
        "exit_code": proc.returncode,
        "stdout": text[:max_chars],
        "stderr": stderr.decode(errors="replace")[:max_chars],
        "files": sorted(set(files)),
        "truncated": len(text) > max_chars,
    }


call = diff_command
