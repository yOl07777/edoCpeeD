from __future__ import annotations

import os
from typing import Any

SYNC_OUTPUT_SUPPORTED = True
_xtversion_name = ""


async def setXtversionName(*args: Any, **kwargs: Any) -> Any:
    global _xtversion_name
    _xtversion_name = str(args[0] if args else kwargs.get("name", ""))
    return _xtversion_name


async def isXtermJs(*args: Any, **kwargs: Any) -> Any:
    name = str(args[0] if args else kwargs.get("name", _xtversion_name or os.environ.get("TERM_PROGRAM", ""))).lower()
    return any(marker in name for marker in ("xterm.js", "vscode", "cursor", "windsurf"))


async def isSynchronizedOutputSupported(*args: Any, **kwargs: Any) -> Any:
    term = str(kwargs.get("term", os.environ.get("TERM", ""))).lower()
    return SYNC_OUTPUT_SUPPORTED and "dumb" not in term


async def isProgressReportingAvailable(*args: Any, **kwargs: Any) -> Any:
    term_program = str(kwargs.get("termProgram", os.environ.get("TERM_PROGRAM", ""))).lower()
    return term_program in {"iterm.app", "vscode", "cursor", "windsurf"}


async def supportsExtendedKeys(*args: Any, **kwargs: Any) -> Any:
    term = str(kwargs.get("term", os.environ.get("TERM", ""))).lower()
    return "xterm" in term or "kitty" in term or await isXtermJs()


async def hasCursorUpViewportYankBug(*args: Any, **kwargs: Any) -> Any:
    term_program = str(kwargs.get("termProgram", os.environ.get("TERM_PROGRAM", ""))).lower()
    return term_program == "apple_terminal"


async def writeDiffToTerminal(*args: Any, **kwargs: Any) -> Any:
    before = str(args[0] if args else kwargs.get("before", ""))
    after = str(args[1] if len(args) > 1 else kwargs.get("after", ""))
    if before == after:
        return ""
    return after
