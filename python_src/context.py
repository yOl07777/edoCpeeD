from __future__ import annotations

import asyncio
import os
import subprocess
from datetime import date
from pathlib import Path
from typing import Any


MAX_STATUS_CHARS = 2000
_system_prompt_injection: str | None = None
_system_context_cache: dict[str, str] | None = None
_user_context_cache: dict[str, str] | None = None


def getSystemPromptInjection() -> str | None:
    return _system_prompt_injection


def setSystemPromptInjection(value: str | None) -> None:
    global _system_prompt_injection, _system_context_cache, _user_context_cache
    _system_prompt_injection = value
    _system_context_cache = None
    _user_context_cache = None


def _run_git(args: list[str], cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    return result.stdout.strip()


async def getGitStatus(cwd: str | os.PathLike[str] | None = None) -> str | None:
    root = Path(cwd or os.getcwd()).resolve()
    try:
        is_git = await asyncio.to_thread(_run_git, ["rev-parse", "--is-inside-work-tree"], root)
        if is_git.lower() != "true":
            return None
        branch, main_branch, status, log, user_name = await asyncio.gather(
            asyncio.to_thread(_run_git, ["branch", "--show-current"], root),
            asyncio.to_thread(_run_git, ["rev-parse", "--abbrev-ref", "origin/HEAD"], root),
            asyncio.to_thread(_run_git, ["--no-optional-locks", "status", "--short"], root),
            asyncio.to_thread(_run_git, ["--no-optional-locks", "log", "--oneline", "-n", "5"], root),
            asyncio.to_thread(_run_git, ["config", "user.name"], root),
        )
    except Exception:
        return None
    if len(status) > MAX_STATUS_CHARS:
        status = status[:MAX_STATUS_CHARS] + '\n... (truncated; run "git status" for full output)'
    return "\n\n".join(
        item
        for item in [
            "This is the git status at the start of the conversation. It is a snapshot and will not update automatically.",
            f"Current branch: {branch or '(detached)'}",
            f"Main branch: {main_branch.removeprefix('origin/') if main_branch else '(unknown)'}",
            f"Git user: {user_name}" if user_name else "",
            f"Status:\n{status or '(clean)'}",
            f"Recent commits:\n{log or '(none)'}",
        ]
        if item
    )


async def getSystemContext(cwd: str | os.PathLike[str] | None = None) -> dict[str, str]:
    global _system_context_cache
    if _system_context_cache is not None:
        return dict(_system_context_cache)
    context: dict[str, str] = {}
    if os.getenv("DEEPSEEK_CODE_DISABLE_GIT_CONTEXT", "").lower() not in {"1", "true", "yes"}:
        git_status = await getGitStatus(cwd)
        if git_status:
            context["gitStatus"] = git_status
    if _system_prompt_injection:
        context["cacheBreaker"] = f"[CACHE_BREAKER: {_system_prompt_injection}]"
    _system_context_cache = context
    return dict(context)


async def getUserContext(cwd: str | os.PathLike[str] | None = None) -> dict[str, str]:
    global _user_context_cache
    if _user_context_cache is not None:
        return dict(_user_context_cache)
    root = Path(cwd or os.getcwd()).resolve()
    context: dict[str, str] = {"currentDate": f"Today's date is {date.today().isoformat()}."}
    if os.getenv("DEEPSEEK_CODE_DISABLE_MEMORY", "").lower() not in {"1", "true", "yes"}:
        for name in ("CLAUDE.md", "DEEPSEEK.md", "AGENTS.md"):
            path = root / name
            if path.exists() and path.is_file():
                context["projectMemory"] = path.read_text(encoding="utf-8", errors="replace")
                break
    _user_context_cache = context
    return dict(context)
