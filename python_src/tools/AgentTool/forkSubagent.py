"""Local fork-subagent shim."""

from __future__ import annotations

import os
from typing import Any

from ._registry import run_agent

FORK_SUBAGENT_TYPE = "fork"
FORK_AGENT: dict[str, Any] = {
    "agentType": FORK_SUBAGENT_TYPE,
    "name": "Fork",
    "description": "Dry-run child agent used for migrated local workflows.",
    "source": "built-in",
}


async def buildChildMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    prompt = kwargs.get("prompt", args[0] if args else "")
    parent_id = kwargs.get("parentRunId") or kwargs.get("parent_run_id")
    return {"role": "user", "content": str(prompt), "parentRunId": parent_id, "fork": True}


async def buildForkedMessages(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    messages = list(kwargs.get("messages") or (args[0] if args else []) or [])
    child = await buildChildMessage(**kwargs)
    return [*messages, child]


async def buildWorktreeNotice(*args: Any, **kwargs: Any) -> str:
    path = kwargs.get("worktree") or kwargs.get("cwd") or (args[0] if args else os.getcwd())
    return f"Forked child agent will run in local dry-run worktree: {path}"


async def isForkSubagentEnabled(*args: Any, **kwargs: Any) -> bool:
    value = kwargs.get("enabled")
    if value is not None:
        return bool(value)
    env = os.getenv("DEEPCODE_ENABLE_FORK_SUBAGENT", "1").strip().lower()
    return env not in {"0", "false", "no", "off"}


async def isInForkChild(*args: Any, **kwargs: Any) -> bool:
    return bool(kwargs.get("forkChild") or os.getenv("DEEPCODE_FORK_CHILD"))


async def forkSubagent(*args: Any, **kwargs: Any) -> dict[str, Any]:
    prompt = str(kwargs.get("prompt") or (args[0] if args else ""))
    return run_agent(FORK_SUBAGENT_TYPE, prompt, status="completed", fork=True)


__all__ = [
    "FORK_AGENT",
    "FORK_SUBAGENT_TYPE",
    "buildChildMessage",
    "buildForkedMessages",
    "buildWorktreeNotice",
    "forkSubagent",
    "isForkSubagentEnabled",
    "isInForkChild",
]
