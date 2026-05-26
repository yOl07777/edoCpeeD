"""Inbound bridge user-message normalization."""

from __future__ import annotations

import base64
from typing import Any


def _detect_image_media_type(data: str) -> str:
    try:
        raw = base64.b64decode(data[:64] + "=" * (-len(data[:64]) % 4))
    except Exception:
        return "image/png"
    if raw.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if raw.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if raw.startswith(b"GIF87a") or raw.startswith(b"GIF89a"):
        return "image/gif"
    if raw.startswith(b"RIFF") and b"WEBP" in raw[:16]:
        return "image/webp"
    return "image/png"


def normalizeImageBlocks(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    changed = False
    normalized: list[dict[str, Any]] = []
    for block in blocks:
        source = block.get("source") if isinstance(block, dict) else None
        if (
            isinstance(block, dict)
            and block.get("type") == "image"
            and isinstance(source, dict)
            and source.get("type") == "base64"
            and not source.get("media_type")
        ):
            media_type = source.get("mediaType")
            if not isinstance(media_type, str) or not media_type:
                media_type = _detect_image_media_type(str(source.get("data", "")))
            new_block = dict(block)
            new_block["source"] = {
                "type": "base64",
                "media_type": media_type,
                "data": source.get("data", ""),
            }
            normalized.append(new_block)
            changed = True
        else:
            normalized.append(block)
    return normalized if changed else blocks


def extractInboundMessageFields(msg: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(msg, dict) or msg.get("type") != "user":
        return None
    message = msg.get("message")
    content = message.get("content") if isinstance(message, dict) else None
    if content is None or content == [] or content == "":
        return None
    uuid = msg.get("uuid") if isinstance(msg.get("uuid"), str) else None
    return {
        "content": normalizeImageBlocks(content) if isinstance(content, list) else content,
        "uuid": uuid,
    }
