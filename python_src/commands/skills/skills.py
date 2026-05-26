"""Local `/skills` command shim."""

from __future__ import annotations

from typing import Any


def _context_commands(context: Any) -> list[dict[str, Any]]:
    if isinstance(context, dict):
        options = context.get("options", {})
        commands = options.get("commands") if isinstance(options, dict) else None
        return [cmd for cmd in commands or [] if isinstance(cmd, dict)]
    options = getattr(context, "options", None)
    commands = getattr(options, "commands", None) if options is not None else None
    return [cmd for cmd in commands or [] if isinstance(cmd, dict)]


def getSkillSummary(context: Any = None) -> dict[str, Any]:
    commands = _context_commands(context)
    skills = [
        {
            "name": cmd.get("name"),
            "description": cmd.get("description", ""),
            "source": cmd.get("source", "unknown"),
        }
        for cmd in commands
        if cmd.get("type") == "prompt" and cmd.get("source") not in {None, "builtin"}
    ]
    return {"type": "skills", "count": len(skills), "skills": skills}


def formatSkillSummary(summary: dict[str, Any]) -> str:
    if summary["count"] == 0:
        return "No project or plugin skills are currently loaded."
    lines = ["Loaded skills:"]
    for skill in summary["skills"]:
        lines.append(f"- /{skill['name']}: {skill['description']}")
    return "\n".join(lines)


async def call(onDone: Any = None, context: Any = None, *_args: Any, **_kwargs: Any) -> dict[str, Any] | None:
    summary = getSkillSummary(context)
    message = formatSkillSummary(summary)
    if callable(onDone):
        try:
            onDone(message, {"display": "system"})
        except TypeError:
            onDone(message)
        return None
    return {"type": "text", "value": message, "skills": summary}
