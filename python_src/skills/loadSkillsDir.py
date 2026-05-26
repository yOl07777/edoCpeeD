"""Skill directory loader for the Python migration."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable

_dynamic_skills: list[dict[str, Any]] = []
_callbacks: list[Callable[[list[dict[str, Any]]], Any]] = []
_conditional_skill_count = 0


def _config_home() -> Path:
    root = os.getenv("DEEPCODE_CONFIG_HOME") or os.getenv("DEEPSEEK_CODE_HOME")
    return Path(root).expanduser().resolve() if root else (Path.home() / ".deepcode").resolve()


async def getSkillsPath(*args: Any, **kwargs: Any) -> str:
    source = str(kwargs.get("source") or (args[0] if args else "userSettings"))
    directory = str(kwargs.get("dir") or kwargs.get("directory") or (args[1] if len(args) > 1 else "skills"))
    if source == "policySettings":
        return str(_config_home() / "managed" / ".deepseek" / directory)
    if source == "userSettings":
        return str(_config_home() / directory)
    if source == "projectSettings":
        return f".deepseek/{directory}"
    if source == "plugin":
        return "plugin"
    return ""


def _parse_frontmatter(markdown: str) -> tuple[dict[str, Any], str]:
    if not markdown.startswith("---"):
        return {}, markdown
    parts = markdown.split("---", 2)
    if len(parts) < 3:
        return {}, markdown
    raw = parts[1]
    body = parts[2].lstrip("\r\n")
    data: dict[str, Any] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            data[key.strip()] = [item.strip().strip("'\"") for item in value[1:-1].split(",") if item.strip()]
        elif value.lower() in {"true", "false"}:
            data[key.strip()] = value.lower() == "true"
        else:
            data[key.strip()] = value.strip("'\"")
    return data, body


async def parseSkillFrontmatterFields(*args: Any, **kwargs: Any) -> dict[str, Any]:
    frontmatter = dict(kwargs.get("frontmatter") or (args[0] if args and isinstance(args[0], dict) else {}))
    markdown = str(kwargs.get("markdownContent") or (args[1] if len(args) > 1 else ""))
    resolved_name = str(kwargs.get("resolvedName") or (args[2] if len(args) > 2 else frontmatter.get("name") or "skill"))
    description = str(frontmatter.get("description") or _extract_description(markdown) or f"Skill {resolved_name}")
    allowed = frontmatter.get("allowed-tools") or frontmatter.get("allowedTools") or []
    if isinstance(allowed, str):
        allowed = [item.strip() for item in allowed.split(",") if item.strip()]
    return {
        "displayName": str(frontmatter["name"]) if frontmatter.get("name") is not None else None,
        "description": description,
        "hasUserSpecifiedDescription": frontmatter.get("description") is not None,
        "allowedTools": list(allowed or []),
        "argumentHint": frontmatter.get("argument-hint"),
        "argumentNames": list(frontmatter.get("arguments") or []),
        "whenToUse": frontmatter.get("when_to_use") or frontmatter.get("whenToUse"),
        "version": frontmatter.get("version"),
        "model": None if frontmatter.get("model") == "inherit" else frontmatter.get("model"),
        "disableModelInvocation": bool(frontmatter.get("disable-model-invocation", False)),
        "userInvocable": bool(frontmatter.get("user-invocable", True)),
        "hooks": frontmatter.get("hooks"),
        "executionContext": "fork" if frontmatter.get("context") == "fork" else None,
        "agent": frontmatter.get("agent"),
        "effort": frontmatter.get("effort"),
        "shell": frontmatter.get("shell"),
    }


def _extract_description(markdown: str) -> str | None:
    for line in markdown.splitlines():
        stripped = line.strip("# ").strip()
        if stripped:
            return stripped[:240]
    return None


async def estimateSkillFrontmatterTokens(*args: Any, **kwargs: Any) -> int:
    skill = kwargs.get("skill") or (args[0] if args else {})
    if not isinstance(skill, dict):
        return 0
    text = " ".join(str(skill.get(key) or "") for key in ("name", "description", "whenToUse"))
    return max(1, len(text) // 4) if text.strip() else 0


async def createSkillCommand(*args: Any, **kwargs: Any) -> dict[str, Any]:
    path = Path(str(kwargs.get("filePath") or kwargs.get("path") or (args[0] if args else "")))
    markdown = kwargs.get("markdownContent")
    if markdown is None:
        markdown = path.read_text(encoding="utf-8") if path.exists() else ""
    frontmatter, body = _parse_frontmatter(str(markdown))
    name = str(kwargs.get("name") or frontmatter.get("name") or path.parent.name or path.stem)
    fields = await parseSkillFrontmatterFields(frontmatter, body, name)

    async def getPromptForCommand(command_args: str = "", context: Any | None = None) -> list[dict[str, str]]:
        text = body
        if command_args:
            text += f"\n\nArguments: {command_args}"
        return [{"type": "text", "text": text}]

    return {
        "type": "prompt",
        "name": name,
        "description": fields["description"],
        "aliases": [],
        "hasUserSpecifiedDescription": fields["hasUserSpecifiedDescription"],
        "allowedTools": fields["allowedTools"],
        "argumentHint": fields["argumentHint"],
        "whenToUse": fields["whenToUse"],
        "model": fields["model"],
        "disableModelInvocation": fields["disableModelInvocation"],
        "userInvocable": fields["userInvocable"],
        "contentLength": len(body),
        "source": str(path),
        "loadedFrom": kwargs.get("loadedFrom") or "skills",
        "skillRoot": str(path.parent) if path else None,
        "progressMessage": "running",
        "getPromptForCommand": getPromptForCommand,
        **{k: v for k, v in fields.items() if k in {"hooks", "agent", "effort", "shell"}},
    }


async def discoverSkillDirsForPaths(*args: Any, **kwargs: Any) -> list[str]:
    paths = kwargs.get("paths") or (args[0] if args else [])
    dirs: list[str] = []
    for item in paths or []:
        path = Path(str(item))
        candidates = [path] if path.is_dir() else [path.parent]
        for base in candidates:
            for skill_file in base.rglob("SKILL.md") if base.exists() else []:
                dirs.append(str(skill_file.parent))
    return sorted(set(dirs))


async def addSkillDirectories(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    dirs = kwargs.get("dirs") or kwargs.get("directories") or (args[0] if args else [])
    loaded: list[dict[str, Any]] = []
    for directory in dirs or []:
        skill_file = Path(str(directory)) / "SKILL.md"
        if skill_file.exists():
            loaded.append(await createSkillCommand(skill_file))
    _dynamic_skills.extend(loaded)
    for callback in list(_callbacks):
        callback(list(_dynamic_skills))
    return loaded


async def activateConditionalSkillsForPaths(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    global _conditional_skill_count
    dirs = await discoverSkillDirsForPaths(kwargs.get("paths") or (args[0] if args else []))
    loaded = await addSkillDirectories(dirs)
    _conditional_skill_count += len(loaded)
    return loaded


async def getDynamicSkills(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    return list(_dynamic_skills)


async def clearDynamicSkills(*args: Any, **kwargs: Any) -> None:
    global _conditional_skill_count
    _dynamic_skills.clear()
    _conditional_skill_count = 0


async def clearSkillCaches(*args: Any, **kwargs: Any) -> None:
    await clearDynamicSkills()


async def getConditionalSkillCount(*args: Any, **kwargs: Any) -> int:
    return _conditional_skill_count


async def onDynamicSkillsLoaded(*args: Any, **kwargs: Any) -> Callable[[], None]:
    callback = kwargs.get("callback") or (args[0] if args else None)
    if callable(callback):
        _callbacks.append(callback)

    def dispose() -> None:
        if callback in _callbacks:
            _callbacks.remove(callback)

    return dispose


async def getSkillDirCommands(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    directory = kwargs.get("directory") or kwargs.get("dir") or (args[0] if args else await getSkillsPath())
    return await addSkillDirectories([directory])


__all__ = [
    "activateConditionalSkillsForPaths",
    "addSkillDirectories",
    "clearDynamicSkills",
    "clearSkillCaches",
    "createSkillCommand",
    "discoverSkillDirsForPaths",
    "estimateSkillFrontmatterTokens",
    "getConditionalSkillCount",
    "getDynamicSkills",
    "getSkillDirCommands",
    "getSkillsPath",
    "onDynamicSkillsLoaded",
    "parseSkillFrontmatterFields",
]
