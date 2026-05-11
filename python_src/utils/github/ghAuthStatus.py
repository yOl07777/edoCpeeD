from __future__ import annotations

import asyncio
from typing import Any


async def _run_gh(*args: str, cwd: str | None = None, timeout: int = 15) -> dict[str, Any]:
    try:
        proc = await asyncio.create_subprocess_exec(
            "gh",
            *args,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except FileNotFoundError:
        return {"available": False, "exit_code": 127, "stdout": "", "stderr": "GitHub CLI `gh` is not installed."}
    except asyncio.TimeoutError:
        return {"available": True, "exit_code": 124, "stdout": "", "stderr": "GitHub CLI command timed out."}
    return {
        "available": True,
        "exit_code": proc.returncode,
        "stdout": stdout.decode(errors="replace"),
        "stderr": stderr.decode(errors="replace"),
    }


async def getGhAuthStatus(cwd: str | None = None) -> dict[str, Any]:
    result = await _run_gh("auth", "status", cwd=cwd)
    text = f"{result['stdout']}\n{result['stderr']}".lower()
    return {
        **result,
        "authenticated": result["exit_code"] == 0 and "not logged" not in text and "failed" not in text,
    }
