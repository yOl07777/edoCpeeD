from __future__ import annotations

from typing import Any

from python_src.components.messages._shared import message_payload, normalize_attachment


async def AttachmentMessage(*args: Any, **kwargs: Any) -> Any:
    attachments = kwargs.get("attachments") or (args[0] if args else []) or []
    if not isinstance(attachments, list):
        attachments = [attachments]
    rows = [normalize_attachment(item, index) for index, item in enumerate(attachments)]
    return message_payload("attachment_message", attachments=rows, count=len(rows))


__all__ = ["AttachmentMessage"]
