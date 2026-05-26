"""Magic Docs tracking and update shim."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Awaitable, Callable

from .prompts import buildMagicDocsUpdatePrompt


MAGIC_DOC_HEADER_PATTERN = re.compile(r"^#\s*MAGIC\s+DOC:\s*(.+)$", re.IGNORECASE | re.MULTILINE)
ITALICS_PATTERN = re.compile(r"^[_*](.+?)[_*]\s*$")
_tracked_magic_docs: dict[str, dict[str, str]] = {}
_initialized = False


def clearTrackedMagicDocs(*_: Any, **__: Any) -> None:
    _tracked_magic_docs.clear()


def getTrackedMagicDocs(*_: Any, **__: Any) -> list[dict[str, str]]:
    return list(_tracked_magic_docs.values())


def detectMagicDocHeader(content: str, *_: Any, **__: Any) -> dict[str, str] | None:
    match = MAGIC_DOC_HEADER_PATTERN.search(content or "")
    if not match:
        return None
    title = match.group(1).strip()
    after = content[match.end() :]
    next_line = re.match(r"^\s*\n(?:\s*\n)?(.+?)(?:\n|$)", after)
    if next_line:
        italics = ITALICS_PATTERN.match(next_line.group(1))
        if italics:
            return {"title": title, "instructions": italics.group(1).strip()}
    return {"title": title}


def registerMagicDoc(filePath: str, *_: Any, **__: Any) -> None:
    path = str(Path(filePath))
    _tracked_magic_docs.setdefault(path, {"path": path})


def _has_tool_calls_in_last_assistant_turn(messages: list[dict[str, Any]]) -> bool:
    for message in reversed(messages):
        if (message.get("type") or message.get("role")) != "assistant":
            continue
        content = (message.get("message") or {}).get("content", message.get("content"))
        blocks = content if isinstance(content, list) else []
        return any(isinstance(block, dict) and block.get("type") in {"tool_use", "tool_call"} for block in blocks)
    return False


async def _default_runner(payload: dict[str, Any]) -> dict[str, Any]:
    callback = payload.get("runAgent")
    if callable(callback):
        result = callback(payload)
        if hasattr(result, "__await__"):
            return await result
        return result
    return {"status": "planned", "prompt": payload["prompt"]}


async def updateMagicDoc(docInfo: dict[str, str], context: dict[str, Any]) -> dict[str, Any] | None:
    path = Path(docInfo["path"])
    try:
        current = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        _tracked_magic_docs.pop(docInfo["path"], None)
        return {"status": "removed", "path": docInfo["path"]}

    detected = detectMagicDocHeader(current)
    if not detected:
        _tracked_magic_docs.pop(docInfo["path"], None)
        return {"status": "untracked", "path": docInfo["path"]}

    prompt = await buildMagicDocsUpdatePrompt(current, docInfo["path"], detected["title"], detected.get("instructions"))

    async def can_use_tool(tool: dict[str, Any] | Any, input: dict[str, Any] | None = None) -> dict[str, Any]:
        name = tool.get("name") if isinstance(tool, dict) else getattr(tool, "name", None)
        file_path = (input or {}).get("file_path")
        if name in {"Edit", "FileEdit"} and file_path == docInfo["path"]:
            return {"behavior": "allow", "updatedInput": input or {}}
        return {
            "behavior": "deny",
            "message": f"only Edit is allowed for {docInfo['path']}",
            "decisionReason": {"type": "other", "reason": "only Edit is allowed"},
        }

    runner = context.get("runAgent")
    result = await _default_runner(
        {
            "agentDefinition": {"agentType": "magic-docs", "model": "deepseek-chat", "tools": ["Edit"]},
            "prompt": prompt,
            "querySource": "magic_docs",
            "canUseTool": can_use_tool,
            "runAgent": runner,
            "docPath": docInfo["path"],
        }
    )
    return {"status": "updated", "path": docInfo["path"], "prompt": prompt, "result": result}


async def updateMagicDocs(context: dict[str, Any] | None = None, *_: Any, **__: Any) -> list[dict[str, Any]]:
    ctx = context or {}
    if ctx.get("querySource") not in {None, "repl_main_thread"}:
        return []
    if _has_tool_calls_in_last_assistant_turn(list(ctx.get("messages") or [])):
        return []
    results = []
    for doc in list(_tracked_magic_docs.values()):
        result = await updateMagicDoc(doc, ctx)
        if result:
            results.append(result)
    return results


async def initMagicDocs(*_: Any, **__: Any) -> dict[str, Any]:
    global _initialized
    _initialized = True
    return {"initialized": True}


__all__ = [
    "clearTrackedMagicDocs",
    "detectMagicDocHeader",
    "getTrackedMagicDocs",
    "initMagicDocs",
    "registerMagicDoc",
    "updateMagicDoc",
    "updateMagicDocs",
]
