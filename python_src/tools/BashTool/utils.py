"""Output helpers for BashTool migration."""

from __future__ import annotations

import base64
import os
import re
from pathlib import Path
from typing import Any

stdErrAppendShellResetMessage = "\n[Shell reset to workspace directory]"


async def stripEmptyLines(*args: Any, **kwargs: Any) -> str:
    text = str(kwargs.get("text") or (args[0] if args else ""))
    lines = text.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)


async def parseDataUri(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    value = str(kwargs.get("value") or kwargs.get("uri") or (args[0] if args else ""))
    match = re.match(r"^data:(?P<mime>[^;,]+)?(?P<base64>;base64)?,(?P<data>.*)$", value, re.DOTALL)
    if not match:
        return None
    payload = match.group("data")
    raw = base64.b64decode(payload) if match.group("base64") else payload.encode("utf-8")
    return {"mimeType": match.group("mime") or "text/plain", "base64": bool(match.group("base64")), "data": raw}


async def isImageOutput(*args: Any, **kwargs: Any) -> bool:
    value = kwargs.get("value") or kwargs.get("output") or (args[0] if args else "")
    if isinstance(value, dict):
        mime = str(value.get("mimeType") or value.get("mime") or "")
        return mime.startswith("image/")
    text = str(value)
    return text.startswith("data:image/") or bool(re.search(r"\.(png|jpe?g|gif|webp|bmp)$", text, re.IGNORECASE))


async def resizeShellImageOutput(*args: Any, **kwargs: Any) -> dict[str, Any]:
    image = args[0] if args else kwargs.get("image", {})
    width = int(kwargs.get("width", 1024))
    height = int(kwargs.get("height", 1024))
    payload = image if isinstance(image, dict) else {"data": image}
    return {**payload, "maxWidth": width, "maxHeight": height, "resized": True}


async def buildImageToolResult(*args: Any, **kwargs: Any) -> dict[str, Any]:
    value = kwargs.get("value") or kwargs.get("output") or (args[0] if args else "")
    parsed = await parseDataUri(value) if isinstance(value, str) else None
    if parsed:
        return {"type": "image", "mimeType": parsed["mimeType"], "bytes": len(parsed["data"])}
    return {"type": "image", "source": str(value)}


async def createContentSummary(*args: Any, **kwargs: Any) -> dict[str, Any]:
    content = str(kwargs.get("content") or kwargs.get("text") or (args[0] if args else ""))
    limit = int(kwargs.get("limit", 2000))
    return {
        "lineCount": 0 if not content else len(content.splitlines()),
        "charCount": len(content),
        "truncated": len(content) > limit,
        "preview": content[:limit],
    }


async def formatOutput(*args: Any, **kwargs: Any) -> dict[str, Any]:
    result = args[0] if args and isinstance(args[0], dict) else kwargs
    stdout = await stripEmptyLines(text=str(result.get("stdout", "")))
    stderr = await stripEmptyLines(text=str(result.get("stderr", "")))
    return {
        "stdout": stdout,
        "stderr": stderr,
        "exitCode": result.get("exit_code", result.get("exitCode", 0)),
        "timedOut": bool(result.get("timed_out", result.get("timedOut", False))),
        "summary": await createContentSummary("\n".join(part for part in [stdout, stderr] if part)),
    }


async def resetCwdIfOutsideProject(*args: Any, **kwargs: Any) -> dict[str, Any]:
    current = Path(kwargs.get("cwd") or (args[0] if args else os.getcwd())).resolve()
    project = Path(kwargs.get("projectRoot") or kwargs.get("project_root") or os.getcwd()).resolve()
    inside = current == project or project in current.parents
    return {"cwd": str(current if inside else project), "reset": not inside, "message": "" if inside else stdErrAppendShellResetMessage}


__all__ = [
    "stdErrAppendShellResetMessage",
    "buildImageToolResult",
    "createContentSummary",
    "formatOutput",
    "isImageOutput",
    "parseDataUri",
    "resetCwdIfOutsideProject",
    "resizeShellImageOutput",
    "stripEmptyLines",
]
