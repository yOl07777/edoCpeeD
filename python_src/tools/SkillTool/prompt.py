"""Prompt helpers for SkillTool."""

from __future__ import annotations

from typing import Any

from python_src.tools.SkillTool.constants import SKILL_TOOL_NAME

CHARS_PER_TOKEN = 4
DEFAULT_CHAR_BUDGET = 20_000
MAX_LISTING_DESC_CHARS = 300
SKILL_BUDGET_CONTEXT_PERCENT = 0.2

_PROMPT_CACHE: dict[str, Any] = {}


def _command_text(command: Any) -> str:
    if isinstance(command, dict):
        name = command.get("name") or command.get("command") or "skill"
        desc = command.get("description") or command.get("summary") or ""
        return f"- {name}: {str(desc)[:MAX_LISTING_DESC_CHARS]}".rstrip()
    return f"- {command}"


async def clearPromptCache(*args: Any, **kwargs: Any) -> dict[str, int]:
    count = len(_PROMPT_CACHE)
    _PROMPT_CACHE.clear()
    return {"cleared": count}


async def getCharBudget(*args: Any, **kwargs: Any) -> int:
    if "charBudget" in kwargs:
        return int(kwargs["charBudget"])
    if "char_budget" in kwargs:
        return int(kwargs["char_budget"])
    tokens = kwargs.get("contextTokens") or kwargs.get("context_tokens")
    if tokens is not None:
        return int(int(tokens) * CHARS_PER_TOKEN * SKILL_BUDGET_CONTEXT_PERCENT)
    return DEFAULT_CHAR_BUDGET


async def formatCommandsWithinBudget(*args: Any, **kwargs: Any) -> str:
    commands = list(args[0] if args else kwargs.get("commands", []) or [])
    budget = int(kwargs.get("budget") or await getCharBudget(**kwargs))
    lines: list[str] = []
    used = 0
    for command in commands:
        line = _command_text(command)
        if used + len(line) + 1 > budget:
            break
        lines.append(line)
        used += len(line) + 1
    return "\n".join(lines)


async def getLimitedSkillToolCommands(*args: Any, **kwargs: Any) -> list[Any]:
    commands = list(args[0] if args else kwargs.get("commands", []) or [])
    budget = int(kwargs.get("budget") or await getCharBudget(**kwargs))
    selected: list[Any] = []
    used = 0
    for command in commands:
        line = _command_text(command)
        if used + len(line) + 1 > budget:
            break
        selected.append(command)
        used += len(line) + 1
    return selected


async def getSkillInfo(*args: Any, **kwargs: Any) -> dict[str, Any]:
    value = args[0] if args else kwargs
    if isinstance(value, dict):
        return {
            "name": value.get("name") or value.get("id") or "skill",
            "description": value.get("description") or value.get("summary") or "",
            "path": value.get("path"),
        }
    return {"name": str(value), "description": "", "path": None}


async def getSkillToolInfo(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return {"name": SKILL_TOOL_NAME, "description": "List or read local workspace skills.", "budget": await getCharBudget(**kwargs)}


async def _getPrompt(*args: Any, **kwargs: Any) -> str:
    commands = list(kwargs.get("commands", []) or (args[0] if args else []) or [])
    formatted = await formatCommandsWithinBudget(commands, **kwargs)
    return (
        "Use the skill tool to list or read local SKILL.md files. "
        "Read only the skill needed for the current task.\n"
        f"{formatted}"
    ).rstrip()


getPrompt = _getPrompt

__all__ = [
    "CHARS_PER_TOKEN",
    "DEFAULT_CHAR_BUDGET",
    "MAX_LISTING_DESC_CHARS",
    "SKILL_BUDGET_CONTEXT_PERCENT",
    "clearPromptCache",
    "formatCommandsWithinBudget",
    "getCharBudget",
    "getLimitedSkillToolCommands",
    "getPrompt",
    "getSkillInfo",
    "getSkillToolInfo",
]
