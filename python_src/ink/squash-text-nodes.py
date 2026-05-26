from __future__ import annotations

from typing import Any


def _walk(node: Any, inherited_style: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    style = dict(inherited_style or {})
    if isinstance(node, str):
        return [{"type": "text", "text": node, "style": style}]
    if isinstance(node, dict):
        style.update(node.get("style", {}) or {})
        if "text" in node or node.get("type") in {"text", "link", "newline"}:
            return [{"type": "text", "text": str(node.get("text", "")), "style": style}]
        segments: list[dict[str, Any]] = []
        for child in node.get("children", []) or []:
            segments.extend(_walk(child, style))
        if node.get("visibleText"):
            segments.append({"type": "text", "text": str(node["visibleText"]), "style": style})
        return segments
    if isinstance(node, (list, tuple)):
        segments: list[dict[str, Any]] = []
        for child in node:
            segments.extend(_walk(child, style))
        return segments
    return [{"type": "text", "text": str(node), "style": style}]


async def squashTextNodesToSegments(*args: Any, **kwargs: Any) -> Any:
    node = args[0] if args else kwargs.get("node", kwargs.get("children", []))
    segments = _walk(node)
    merged: list[dict[str, Any]] = []
    for segment in segments:
        if merged and merged[-1]["style"] == segment["style"]:
            merged[-1]["text"] += segment["text"]
        else:
            merged.append(segment)
    return merged
