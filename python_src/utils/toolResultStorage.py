"""Local tool result persistence and budget helpers."""

from __future__ import annotations

import json
import re
import uuid
from copy import deepcopy
from pathlib import Path
from typing import Any

PERSISTED_OUTPUT_TAG = "persisted-tool-output"
PERSISTED_OUTPUT_CLOSING_TAG = f"/{PERSISTED_OUTPUT_TAG}"
PREVIEW_SIZE_BYTES = 4_000
TOOL_RESULTS_SUBDIR = ".deepseek_tool_results"
TOOL_RESULT_CLEARED_MESSAGE = "[tool result content cleared]"


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    if args and isinstance(args[0], dict):
        return {**args[0], **kwargs}
    if args:
        return {"content": args[0], **kwargs}
    return dict(kwargs)


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, ensure_ascii=False, indent=2)
    except TypeError:
        return str(value)


async def getToolResultsDir(*args: Any, **kwargs: Any) -> str:
    base = Path(args[0] if args else kwargs.get("base_dir") or kwargs.get("baseDir") or ".").expanduser()
    return str(base / TOOL_RESULTS_SUBDIR)


async def ensureToolResultsDir(*args: Any, **kwargs: Any) -> str:
    path = Path(await getToolResultsDir(*args, **kwargs))
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


async def getToolResultPath(*args: Any, **kwargs: Any) -> str:
    data = _payload(args, kwargs)
    result_id = str(data.get("id") or data.get("tool_use_id") or data.get("toolUseId") or uuid.uuid4().hex)
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", result_id).strip(".-") or "tool-result"
    directory = Path(await ensureToolResultsDir(base_dir=data.get("base_dir") or data.get("baseDir") or "."))
    return str(directory / f"{safe}.txt")


async def getPersistenceThreshold(*args: Any, **kwargs: Any) -> int:
    return int(kwargs.get("threshold") or kwargs.get("bytes") or kwargs.get("max_inline_bytes") or 12_000)


async def getPerMessageBudgetLimit(*args: Any, **kwargs: Any) -> int:
    return int(kwargs.get("limit") or kwargs.get("budget") or kwargs.get("max_chars") or 20_000)


async def generatePreview(*args: Any, **kwargs: Any) -> str:
    data = _payload(args, kwargs)
    content = _text(data.get("content"))
    max_bytes = int(data.get("preview_size") or data.get("previewSize") or PREVIEW_SIZE_BYTES)
    encoded = content.encode("utf-8")
    if len(encoded) <= max_bytes:
        return content
    return encoded[:max_bytes].decode("utf-8", errors="ignore") + "\n...[truncated]"


async def isToolResultContentEmpty(*args: Any, **kwargs: Any) -> bool:
    content = _text(args[0] if args else kwargs.get("content"))
    return content.strip() == ""


async def isPersistError(*args: Any, **kwargs: Any) -> bool:
    value = args[0] if args else kwargs.get("error")
    return isinstance(value, (OSError, IOError, PermissionError))


async def persistToolResult(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    content = _text(data.get("content"))
    path = Path(data.get("path") or await getToolResultPath(**data))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    preview = await generatePreview(content=content, preview_size=data.get("preview_size") or data.get("previewSize") or PREVIEW_SIZE_BYTES)
    return {
        "path": str(path),
        "bytes": len(content.encode("utf-8")),
        "preview": preview,
        "tag": f"<{PERSISTED_OUTPUT_TAG} path=\"{path}\" bytes=\"{len(content.encode('utf-8'))}\">",
    }


async def buildLargeToolResultMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    persisted = await persistToolResult(*args, **kwargs)
    return {
        "type": "large-tool-result",
        "content": f"{persisted['tag']}\n{persisted['preview']}\n<{PERSISTED_OUTPUT_CLOSING_TAG}>",
        "path": persisted["path"],
        "bytes": persisted["bytes"],
        "preview": persisted["preview"],
    }


async def applyToolResultBudget(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    content = _text(data.get("content"))
    limit = int(data.get("limit") or await getPerMessageBudgetLimit(**data))
    if len(content) <= limit:
        return {"content": content, "truncated": False, "original_bytes": len(content.encode("utf-8"))}
    return {
        "content": content[:limit],
        "truncated": True,
        "original_bytes": len(content.encode("utf-8")),
        "truncated_bytes": len(content[limit:].encode("utf-8")),
    }


async def enforceToolResultBudget(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    content = _text(data.get("content"))
    threshold = int(data.get("threshold") or await getPersistenceThreshold(**data))
    if len(content.encode("utf-8")) <= threshold:
        return {"persisted": False, "content": content}
    large = await buildLargeToolResultMessage(**data)
    return {"persisted": True, **large}


async def createContentReplacementState(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return {"replacements": {}, "cleared": [], "version": 1}


async def cloneContentReplacementState(*args: Any, **kwargs: Any) -> dict[str, Any]:
    state = args[0] if args else kwargs.get("state") or {}
    return deepcopy(state)


async def provisionContentReplacementState(*args: Any, **kwargs: Any) -> dict[str, Any]:
    state = args[0] if args else kwargs.get("state")
    return deepcopy(state) if isinstance(state, dict) else await createContentReplacementState()


async def reconstructContentReplacementState(*args: Any, **kwargs: Any) -> dict[str, Any]:
    state = await provisionContentReplacementState(*args, **kwargs)
    for replacement in kwargs.get("replacements", []) or []:
        if isinstance(replacement, dict) and replacement.get("id"):
            state.setdefault("replacements", {})[replacement["id"]] = replacement
    return state


async def reconstructForSubagentResume(*args: Any, **kwargs: Any) -> dict[str, Any]:
    state = await reconstructContentReplacementState(*args, **kwargs)
    state["subagent_resume"] = True
    return state


async def processToolResultBlock(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    return await enforceToolResultBudget(**data)


async def processPreMappedToolResultBlock(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    if data.get("path"):
        return {"persisted": True, "path": str(data["path"]), "content": data.get("content", "")}
    return await processToolResultBlock(**data)


__all__ = [
    "PERSISTED_OUTPUT_CLOSING_TAG",
    "PERSISTED_OUTPUT_TAG",
    "PREVIEW_SIZE_BYTES",
    "TOOL_RESULTS_SUBDIR",
    "TOOL_RESULT_CLEARED_MESSAGE",
    "applyToolResultBudget",
    "buildLargeToolResultMessage",
    "cloneContentReplacementState",
    "createContentReplacementState",
    "enforceToolResultBudget",
    "ensureToolResultsDir",
    "generatePreview",
    "getPerMessageBudgetLimit",
    "getPersistenceThreshold",
    "getToolResultPath",
    "getToolResultsDir",
    "isPersistError",
    "isToolResultContentEmpty",
    "persistToolResult",
    "processPreMappedToolResultBlock",
    "processToolResultBlock",
    "provisionContentReplacementState",
    "reconstructContentReplacementState",
    "reconstructForSubagentResume",
]
