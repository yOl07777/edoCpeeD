from __future__ import annotations

import json
from typing import Any

from deepseek_code.core.types import InternalMessage


def _content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    parts.append(str(item.get("text", "")))
                elif item.get("type") in {"image", "image_url"}:
                    parts.append("[image]")
                else:
                    parts.append(json.dumps(item, ensure_ascii=False))
            else:
                parts.append(str(item))
        return "\n".join(part for part in parts if part)
    if content is None:
        return ""
    return str(content)


async def toInternalMessages(messages: list[dict[str, Any] | InternalMessage]) -> list[InternalMessage]:
    internal: list[InternalMessage] = []
    for message in messages:
        if isinstance(message, InternalMessage):
            internal.append(message)
            continue
        role = str(message.get("role", "user"))
        if role not in {"system", "user", "assistant", "tool"}:
            role = "user"
        internal.append(
            InternalMessage(
                role=role,
                content=_content_to_text(message.get("content", "")),
                name=message.get("name"),
                tool_call_id=message.get("tool_call_id"),
            )
        )
    return internal


async def toSDKMessages(messages: list[dict[str, Any] | InternalMessage]) -> list[dict[str, Any]]:
    sdk = []
    for message in await toInternalMessages(messages):
        item: dict[str, Any] = {"role": message.role, "content": message.content}
        if message.name:
            item["name"] = message.name
        if message.tool_call_id:
            item["tool_call_id"] = message.tool_call_id
        sdk.append(item)
    return sdk


async def localCommandOutputToSDKAssistantMessage(output: Any, *, command: str | None = None) -> dict[str, Any]:
    if isinstance(output, dict):
        text = output.get("stdout") or output.get("output") or json.dumps(output, ensure_ascii=False)
    else:
        text = str(output)
    prefix = f"Command `{command}` output:\n" if command else "Command output:\n"
    return {"role": "assistant", "content": prefix + text}


async def toSDKCompactMetadata(metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(metadata or {})
    payload.setdefault("format", "deepseek_code_compact")
    payload.setdefault("version", 1)
    return payload


async def fromSDKCompactMetadata(metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    return dict(metadata or {})


async def toSDKRateLimitInfo(info: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(info or {})
    return {
        "limit": payload.get("limit"),
        "remaining": payload.get("remaining"),
        "reset": payload.get("reset"),
    }
