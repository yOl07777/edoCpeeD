"""Bundled skill registry for the Python migration."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Awaitable, Callable

_bundled_skills: list[dict[str, Any]] = []


def _config_home() -> Path:
    root = os.getenv("DEEPCODE_CONFIG_HOME") or os.getenv("DEEPSEEK_CODE_HOME")
    return Path(root).expanduser().resolve() if root else (Path.home() / ".deepcode").resolve()


async def getBundledSkillExtractDir(*args: Any, **kwargs: Any) -> str:
    skill_name = str(kwargs.get("skillName") or kwargs.get("name") or (args[0] if args else "skill"))
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in skill_name).strip("-") or "skill"
    return str(_config_home() / "bundled-skills" / safe)


def _prompt_blocks(text: str) -> list[dict[str, str]]:
    return [{"type": "text", "text": text}]


async def _maybe_await(value: Any) -> Any:
    if hasattr(value, "__await__"):
        return await value
    return value


async def _write_reference_files(skill_name: str, files: dict[str, str] | None) -> str | None:
    if not files:
        return None
    base = Path(await getBundledSkillExtractDir(skill_name))
    for rel, content in files.items():
        target = (base / rel).resolve()
        if base not in target.parents and target != base:
            raise ValueError(f"bundled skill file path escapes skill dir: {rel}")
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_text(str(content), encoding="utf-8")
    return str(base)


async def registerBundledSkill(*args: Any, **kwargs: Any) -> dict[str, Any]:
    definition = dict(kwargs.get("definition") or (args[0] if args and isinstance(args[0], dict) else kwargs))
    name = str(definition.get("name") or "skill")
    description = str(definition.get("description") or f"{name} bundled skill")
    files = definition.get("files") if isinstance(definition.get("files"), dict) else None
    prompt_fn: Callable[..., Any] | None = definition.get("getPromptForCommand")

    async def getPromptForCommand(command_args: str = "", context: Any | None = None) -> list[dict[str, Any]]:
        base_dir = await _write_reference_files(name, files)
        if callable(prompt_fn):
            blocks = await _maybe_await(prompt_fn(command_args, context))
            if not isinstance(blocks, list):
                blocks = _prompt_blocks(str(blocks))
        else:
            blocks = _prompt_blocks(f"Run the bundled skill '{name}'.\n\nArguments: {command_args}".strip())
        if base_dir:
            prefix = f"Base directory for this skill: {base_dir}\n\n"
            if blocks and isinstance(blocks[0], dict) and blocks[0].get("type") == "text":
                blocks = [{**blocks[0], "text": prefix + str(blocks[0].get("text", ""))}, *blocks[1:]]
            else:
                blocks = [{"type": "text", "text": prefix}, *blocks]
        return blocks

    skill = {
        "type": "prompt",
        "name": name,
        "description": description,
        "aliases": list(definition.get("aliases") or []),
        "hasUserSpecifiedDescription": True,
        "allowedTools": list(definition.get("allowedTools") or []),
        "argumentHint": definition.get("argumentHint"),
        "whenToUse": definition.get("whenToUse"),
        "model": definition.get("model"),
        "disableModelInvocation": bool(definition.get("disableModelInvocation", False)),
        "userInvocable": bool(definition.get("userInvocable", True)),
        "contentLength": 0,
        "source": "bundled",
        "loadedFrom": "bundled",
        "hooks": definition.get("hooks"),
        "skillRoot": await getBundledSkillExtractDir(name) if files else None,
        "context": definition.get("context"),
        "agent": definition.get("agent"),
        "isEnabled": definition.get("isEnabled"),
        "isHidden": not bool(definition.get("userInvocable", True)),
        "progressMessage": "running",
        "getPromptForCommand": getPromptForCommand,
    }
    _bundled_skills.append(skill)
    return skill


async def getBundledSkills(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    return list(_bundled_skills)


async def clearBundledSkills(*args: Any, **kwargs: Any) -> None:
    _bundled_skills.clear()


__all__ = [
    "clearBundledSkills",
    "getBundledSkillExtractDir",
    "getBundledSkills",
    "registerBundledSkill",
]
