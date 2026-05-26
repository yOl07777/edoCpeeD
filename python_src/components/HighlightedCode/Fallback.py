from __future__ import annotations

from typing import Any


async def HighlightedCodeFallback(*args: Any, **kwargs: Any) -> Any:
    code = str(kwargs.get("code") or (args[0] if args else "") or "")
    language = str(kwargs.get("language") or kwargs.get("lang") or "text")
    lines = code.splitlines()
    return {
        "type": "highlighted_code_fallback",
        "provider": "deepseek",
        "language": language,
        "lineCount": len(lines),
        "lines": [{"number": index + 1, "text": line} for index, line in enumerate(lines)],
    }


__all__ = ["HighlightedCodeFallback"]
