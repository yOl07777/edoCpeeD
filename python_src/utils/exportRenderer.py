"""Render migrated message objects to plain text for `/export`."""

from __future__ import annotations

from typing import Any, Iterable


def _content_to_text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    parts.append(str(item.get("text", "")))
                elif item.get("type") in {"tool_use", "tool_result"}:
                    parts.append(f"[{item.get('type')}: {item.get('name') or item.get('tool_use_id') or ''}]")
                elif "content" in item:
                    parts.append(_content_to_text(item.get("content")))
            else:
                parts.append(str(item))
        return "\n".join(part for part in parts if part)
    if isinstance(content, dict):
        if "text" in content:
            return str(content["text"])
        if "content" in content:
            return _content_to_text(content["content"])
    return str(content)


def _message_role(message: dict[str, Any]) -> str:
    return str(message.get("role") or message.get("type") or "message")


async def renderMessagesToPlainText(messages: Iterable[dict[str, Any]] | None = None, tools: Iterable[Any] | None = None) -> str:
    rendered: list[str] = []
    for message in messages or []:
        if not isinstance(message, dict):
            rendered.append(str(message))
            continue
        role = _message_role(message)
        payload = message.get("message", message)
        content = payload.get("content") if isinstance(payload, dict) else payload
        rendered.append(f"{role.upper()}:\n{_content_to_text(content)}".rstrip())
    if tools:
        names = [str(tool.get("name") if isinstance(tool, dict) else getattr(tool, "name", tool)) for tool in tools]
        rendered.append("TOOLS:\n" + ", ".join(sorted(name for name in names if name)))
    return "\n\n".join(part for part in rendered if part)


async def streamRenderedMessages(messages: Iterable[dict[str, Any]] | None = None, tools: Iterable[Any] | None = None):
    text = await renderMessagesToPlainText(messages, tools)
    for line in text.splitlines(True):
        yield line
