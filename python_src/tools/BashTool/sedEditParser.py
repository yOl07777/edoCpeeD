"""Small sed edit parser used by migrated BashTool checks."""

from __future__ import annotations

import shlex
from typing import Any


def _argv(command: str) -> list[str]:
    try:
        return shlex.split(command, posix=True)
    except ValueError:
        return []


def _find_expression(argv: list[str]) -> str | None:
    for index, token in enumerate(argv[1:], start=1):
        if token in {"-e", "--expression"} and index + 1 < len(argv):
            return argv[index + 1]
        if token.startswith("-e") and len(token) > 2:
            return token[2:]
        if token.startswith("s") and len(token) > 2:
            return token
    return None


def _split_substitution(expression: str) -> dict[str, str] | None:
    if len(expression) < 4 or expression[0] != "s":
        return None
    delimiter = expression[1]
    parts: list[str] = []
    current: list[str] = []
    escaped = False
    for char in expression[2:]:
        if escaped:
            current.append(char)
            escaped = False
            continue
        if char == "\\":
            escaped = True
            current.append(char)
            continue
        if char == delimiter and len(parts) < 2:
            parts.append("".join(current))
            current = []
            continue
        current.append(char)
    parts.append("".join(current))
    if len(parts) != 3:
        return None
    return {"pattern": parts[0], "replacement": parts[1], "flags": parts[2]}


async def isSedInPlaceEdit(*args: Any, **kwargs: Any) -> bool:
    command = str(kwargs.get("command") or (args[0] if args else ""))
    argv = _argv(command)
    return bool(argv and argv[0] == "sed" and any(arg in {"-i", "--in-place"} or arg.startswith("-i") for arg in argv[1:]))


async def parseSedEditCommand(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    command = str(kwargs.get("command") or (args[0] if args else ""))
    argv = _argv(command)
    if not argv or argv[0] != "sed":
        return None
    expression = _find_expression(argv)
    if not expression:
        return None
    substitution = _split_substitution(expression)
    if not substitution:
        return {"command": command, "expression": expression, "inPlace": await isSedInPlaceEdit(command), "valid": False}
    files = [arg for arg in argv[1:] if not arg.startswith("-") and arg != expression and not arg.startswith("s/")]
    return {
        "command": command,
        "expression": expression,
        "pattern": substitution["pattern"],
        "replacement": substitution["replacement"],
        "flags": substitution["flags"],
        "global": "g" in substitution["flags"],
        "inPlace": await isSedInPlaceEdit(command),
        "files": files,
        "valid": True,
    }


async def applySedSubstitution(*args: Any, **kwargs: Any) -> str:
    text = str(kwargs.get("text") or (args[0] if args else ""))
    expression = str(kwargs.get("expression") or (args[1] if len(args) > 1 else ""))
    parsed = await parseSedEditCommand(f"sed -e {shlex.quote(expression)}")
    if not parsed or not parsed.get("valid"):
        return text
    count = 0 if parsed["global"] else 1
    import re

    return re.sub(parsed["pattern"], parsed["replacement"], text, count=count)


__all__ = ["applySedSubstitution", "isSedInPlaceEdit", "parseSedEditCommand"]
