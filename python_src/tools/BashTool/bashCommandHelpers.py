"""Helpers for checking compound bash command permissions."""

from __future__ import annotations

import shlex
from typing import Any

from .bashPermissions import bashToolHasPermission


def _split_segments(command: str) -> list[str]:
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        return [command.strip()]

    segments: list[list[str]] = [[]]
    for token in tokens:
        if token in {";", "&&", "||", "|"}:
            if segments[-1]:
                segments.append([])
            continue
        segments[-1].append(token)
    return [" ".join(shlex.quote(part) for part in segment) for segment in segments if segment]


async def checkCommandOperatorPermissions(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Check each segment of a compound command with the local permission shim."""

    command = str(kwargs.get("command") or (args[0] if args else ""))
    rules = kwargs.get("rules") or kwargs.get("allowed_commands") or []
    read_only_mode = bool(kwargs.get("read_only_mode") or kwargs.get("readOnlyMode", False))
    checks = []
    for segment in _split_segments(command):
        result = await bashToolHasPermission(segment, rules=rules, read_only_mode=read_only_mode)
        checks.append({"command": segment, **result})
    return {"allowed": all(check["allowed"] for check in checks), "checks": checks}


__all__ = ["checkCommandOperatorPermissions"]
