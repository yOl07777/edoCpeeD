from __future__ import annotations

import os
import shlex
from collections.abc import Callable
from pathlib import Path
from typing import Any


COMMAND_OPERATION_TYPE = {
    "cat": "read",
    "cp": "write",
    "grep": "read",
    "head": "read",
    "ls": "read",
    "mkdir": "write",
    "mv": "write",
    "rm": "delete",
    "sed": "write",
    "tail": "read",
    "touch": "write",
}
PATH_EXTRACTORS = {"default": "argv"}


def stripWrappersFromArgv(argv: list[str]) -> list[str]:
    cleaned = list(argv)
    while cleaned and cleaned[0] in {"env", "command", "builtin", "time"}:
        cleaned.pop(0)
    return cleaned


def _paths_from_command(command: str) -> list[str]:
    try:
        argv = stripWrappersFromArgv(shlex.split(command, posix=True))
    except ValueError:
        return []
    paths: list[str] = []
    for token in argv[1:]:
        if token.startswith("-") or "=" in token and not token.startswith((".", "/", "~")):
            continue
        if any(sep in token for sep in ("/", "\\")) or token.startswith((".", "~")):
            paths.append(token)
    return paths


def createPathChecker(
    *,
    cwd: str | os.PathLike[str] | None = None,
    allowed_roots: list[str | os.PathLike[str]] | None = None,
) -> Callable[[str], bool]:
    root = Path(cwd or os.getcwd()).resolve()
    roots = [Path(path).resolve() for path in (allowed_roots or [root])]

    def check(raw_path: str) -> bool:
        expanded = Path(os.path.expanduser(raw_path))
        path = expanded if expanded.is_absolute() else root / expanded
        resolved = path.resolve(strict=False)
        return any(resolved == allowed or allowed in resolved.parents for allowed in roots)

    return check


def checkPathConstraints(
    command: str,
    *,
    cwd: str | os.PathLike[str] | None = None,
    allowed_roots: list[str | os.PathLike[str]] | None = None,
) -> dict[str, Any]:
    check = createPathChecker(cwd=cwd, allowed_roots=allowed_roots)
    denied = [path for path in _paths_from_command(command) if not check(path)]
    return {"ok": not denied, "denied_paths": denied}
