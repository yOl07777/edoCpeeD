"""Small wrappers for operations that were tracked as slow in TypeScript."""

from __future__ import annotations

import copy
import json
import os
import traceback
from contextlib import nullcontext
from pathlib import Path
from typing import Any

SLOW_OPERATION_THRESHOLD_MS = float(os.getenv("CLAUDE_CODE_SLOW_OPERATION_THRESHOLD_MS", "inf"))
slowLogging = lambda *_args, **_kwargs: nullcontext()


def callerFrame(stack: str | None = None) -> str:
    lines = (stack or "".join(traceback.format_stack())).splitlines()
    for line in lines:
        if "slowOperations" in line:
            continue
        stripped = line.strip()
        if stripped:
            return " @ " + stripped
    return ""


def jsonStringify(value: Any, replacer: Any = None, space: int | str | None = None) -> str:
    indent = space if isinstance(space, int) else None
    return json.dumps(value, ensure_ascii=False, indent=indent, default=str)


def jsonParse(text: str, *_args: Any, **_kwargs: Any) -> Any:
    return json.loads(text)


def clone(value: Any, *_args: Any, **_kwargs: Any) -> Any:
    return copy.deepcopy(value)


def cloneDeep(value: Any) -> Any:
    return copy.deepcopy(value)


def writeFileSync_DEPRECATED(filePath: str | os.PathLike[str], data: str | bytes, options: dict[str, Any] | None = None) -> None:
    opts = options or {}
    path = Path(filePath)
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "wb" if isinstance(data, (bytes, bytearray)) else "w"
    encoding = None if "b" in mode else str(opts.get("encoding") or "utf-8")
    with path.open(mode, encoding=encoding) as handle:
        handle.write(data)
        if opts.get("flush"):
            handle.flush()
            try:
                os.fsync(handle.fileno())
            except OSError:
                pass
