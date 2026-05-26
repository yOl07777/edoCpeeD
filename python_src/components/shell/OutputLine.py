from __future__ import annotations

import json
import re
from typing import Any

from python_src.components.shell._shared import shell_payload


async def stripUnderlineAnsi(*args: Any, **kwargs: Any) -> Any:
    text = str(kwargs.get("text") or (args[0] if args else "") or "")
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


async def linkifyUrlsInText(*args: Any, **kwargs: Any) -> Any:
    text = str(kwargs.get("text") or (args[0] if args else "") or "")
    urls = re.findall(r"https?://[^\s)]+", text)
    return {"text": text, "urls": urls}


async def tryFormatJson(*args: Any, **kwargs: Any) -> Any:
    text = str(kwargs.get("text") or (args[0] if args else "") or "")
    try:
        return json.dumps(json.loads(text), indent=2, ensure_ascii=False)
    except Exception:
        return text


async def tryJsonFormatContent(*args: Any, **kwargs: Any) -> Any:
    return await tryFormatJson(*args, **kwargs)


def _is_json(text: str) -> bool:
    try:
        json.loads(text)
        return True
    except Exception:
        return False


async def OutputLine(*args: Any, **kwargs: Any) -> Any:
    text = str(kwargs.get("text") or (args[0] if args else "") or "")
    clean = await stripUnderlineAnsi(text)
    linked = await linkifyUrlsInText(clean)
    return shell_payload("shell_output_line", text=clean, urls=linked["urls"], isJson=_is_json(clean))


__all__ = ["OutputLine", "linkifyUrlsInText", "stripUnderlineAnsi", "tryFormatJson", "tryJsonFormatContent"]
