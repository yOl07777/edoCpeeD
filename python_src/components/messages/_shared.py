from __future__ import annotations

from typing import Any


def message_payload(component: str, **kwargs: Any) -> dict[str, Any]:
    payload = {"type": component, "provider": "deepseek"}
    payload.update(kwargs)
    return payload


def text_from(value: Any = None, **kwargs: Any) -> str:
    if "text" in kwargs and kwargs["text"] is not None:
        return str(kwargs["text"])
    if "content" in kwargs and kwargs["content"] is not None:
        return str(kwargs["content"])
    if isinstance(value, dict):
        return str(value.get("text", value.get("content", "")))
    if value is None:
        return ""
    return str(value)


def normalize_attachment(value: Any, index: int = 0) -> dict[str, Any]:
    if isinstance(value, dict):
        name = value.get("name") or value.get("path") or value.get("url") or f"attachment-{index}"
        kind = value.get("type") or value.get("kind") or "file"
        size = value.get("size") or value.get("bytes")
    else:
        name = str(value)
        kind = "file"
        size = None
    return {"index": index, "name": str(name), "kind": str(kind), "size": size}

