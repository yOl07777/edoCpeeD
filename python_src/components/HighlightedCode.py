from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, scalar_arg


async def HighlightedCode(*args: Any, **kwargs: Any) -> Any:
    code = str(option(args, kwargs, "code", scalar_arg(args, "")))
    language = str(option(args, kwargs, "language", option(args, kwargs, "lang", "")))
    lines = code.splitlines()
    return component_payload("highlighted_code", code=code, language=language, lines=lines, lineCount=len(lines))


__all__ = ["HighlightedCode"]
