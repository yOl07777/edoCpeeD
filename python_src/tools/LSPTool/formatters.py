"""LSP result formatters for local Python migration."""

from __future__ import annotations

from typing import Any


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any:
    if args:
        if isinstance(args[0], dict):
            return {**args[0], **kwargs}
        if isinstance(args[0], list):
            return args[0]
    return dict(kwargs)


def _items(value: Any, key: str = "results") -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        raw = value.get(key) or value.get("items") or value.get("symbols") or value.get("locations") or []
        return raw if isinstance(raw, list) else [raw]
    return [] if value is None else [value]


def _location(item: Any) -> dict[str, Any]:
    if not isinstance(item, dict):
        return {"path": None, "line": None, "character": None, "text": str(item)}
    return {
        "path": item.get("path") or item.get("uri") or item.get("file"),
        "line": item.get("line") or item.get("lineNumber"),
        "character": item.get("character") or item.get("column"),
        "symbol": item.get("symbol") or item.get("name"),
        "text": item.get("text") or item.get("detail") or item.get("containerName"),
    }


async def formatWorkspaceSymbolResult(*args: Any, **kwargs: Any) -> dict[str, Any]:
    value = _payload(args, kwargs)
    symbols = [_location(item) for item in _items(value, "results")]
    return {"type": "workspace-symbols", "count": len(symbols), "symbols": symbols}


async def formatDocumentSymbolResult(*args: Any, **kwargs: Any) -> dict[str, Any]:
    value = _payload(args, kwargs)
    symbols = [_location(item) for item in _items(value, "symbols")]
    return {"type": "document-symbols", "count": len(symbols), "symbols": symbols}


async def formatGoToDefinitionResult(*args: Any, **kwargs: Any) -> dict[str, Any]:
    value = _payload(args, kwargs)
    locations = [_location(item) for item in _items(value, "locations")]
    return {"type": "definition", "count": len(locations), "locations": locations}


async def formatFindReferencesResult(*args: Any, **kwargs: Any) -> dict[str, Any]:
    value = _payload(args, kwargs)
    references = [_location(item) for item in _items(value, "references")]
    return {"type": "references", "count": len(references), "references": references}


async def formatHoverResult(*args: Any, **kwargs: Any) -> dict[str, Any]:
    value = _payload(args, kwargs)
    contents = value.get("contents") if isinstance(value, dict) else value
    if isinstance(contents, dict):
        text = contents.get("value") or contents.get("text") or str(contents)
    elif isinstance(contents, list):
        text = "\n".join(str(item.get("value") if isinstance(item, dict) else item) for item in contents)
    else:
        text = str(contents or "")
    return {"type": "hover", "contents": text}


async def formatPrepareCallHierarchyResult(*args: Any, **kwargs: Any) -> dict[str, Any]:
    value = _payload(args, kwargs)
    items = [_location(item) for item in _items(value, "items")]
    return {"type": "call-hierarchy-items", "count": len(items), "items": items}


async def formatIncomingCallsResult(*args: Any, **kwargs: Any) -> dict[str, Any]:
    value = _payload(args, kwargs)
    calls = [_location(item.get("from") if isinstance(item, dict) and "from" in item else item) for item in _items(value, "calls")]
    return {"type": "incoming-calls", "count": len(calls), "calls": calls}


async def formatOutgoingCallsResult(*args: Any, **kwargs: Any) -> dict[str, Any]:
    value = _payload(args, kwargs)
    calls = [_location(item.get("to") if isinstance(item, dict) and "to" in item else item) for item in _items(value, "calls")]
    return {"type": "outgoing-calls", "count": len(calls), "calls": calls}


__all__ = [
    "formatDocumentSymbolResult",
    "formatFindReferencesResult",
    "formatGoToDefinitionResult",
    "formatHoverResult",
    "formatIncomingCallsResult",
    "formatOutgoingCallsResult",
    "formatPrepareCallHierarchyResult",
    "formatWorkspaceSymbolResult",
]
