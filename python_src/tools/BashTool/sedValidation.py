"""Validation helpers for sed commands."""

from __future__ import annotations

import re
import shlex
from typing import Any


def _argv(command: str) -> list[str]:
    try:
        return shlex.split(command, posix=True)
    except ValueError:
        return []


async def extractSedExpressions(*args: Any, **kwargs: Any) -> list[str]:
    command = str(kwargs.get("command") or (args[0] if args else ""))
    argv = _argv(command)
    expressions: list[str] = []
    for index, token in enumerate(argv):
        if token in {"-e", "--expression"} and index + 1 < len(argv):
            expressions.append(argv[index + 1])
        elif token.startswith("-e") and len(token) > 2:
            expressions.append(token[2:])
        elif token.startswith(("s/", "s#", "s|")) or re.match(r"^\d*,?\d*p$", token):
            expressions.append(token)
    return expressions


async def hasFileArgs(*args: Any, **kwargs: Any) -> bool:
    command = str(kwargs.get("command") or (args[0] if args else ""))
    argv = _argv(command)
    expressions = set(await extractSedExpressions(command))
    for token in argv[1:]:
        if token.startswith("-") or token in expressions:
            continue
        return True
    return False


async def isPrintCommand(*args: Any, **kwargs: Any) -> bool:
    expression = str(kwargs.get("expression") or (args[0] if args else ""))
    return expression == "p" or expression.endswith("p")


async def isLinePrintingCommand(*args: Any, **kwargs: Any) -> bool:
    expression = str(kwargs.get("expression") or (args[0] if args else ""))
    return bool(re.match(r"^\d+(,\d+)?p$", expression))


async def sedCommandIsAllowedByAllowlist(*args: Any, **kwargs: Any) -> bool:
    command = str(kwargs.get("command") or (args[0] if args else ""))
    expressions = await extractSedExpressions(command)
    if not expressions:
        return False
    for expression in expressions:
        if not (await isPrintCommand(expression) or expression.startswith("s")):
            return False
    return True


async def checkSedConstraints(*args: Any, **kwargs: Any) -> dict[str, Any]:
    command = str(kwargs.get("command") or (args[0] if args else ""))
    argv = _argv(command)
    in_place = any(arg in {"-i", "--in-place"} or arg.startswith("-i") for arg in argv)
    expressions = await extractSedExpressions(command)
    allowed = bool(argv and argv[0] == "sed" and not in_place and await sedCommandIsAllowedByAllowlist(command))
    return {
        "ok": allowed,
        "expressions": expressions,
        "hasFileArgs": await hasFileArgs(command),
        "reason": None if allowed else "Sed command is not in the migrated allowlist.",
    }


__all__ = [
    "checkSedConstraints",
    "extractSedExpressions",
    "hasFileArgs",
    "isLinePrintingCommand",
    "isPrintCommand",
    "sedCommandIsAllowedByAllowlist",
]
