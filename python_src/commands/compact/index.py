from __future__ import annotations

from typing import Any

from python_src.services.compact.compact import compactConversation, partialCompactConversation


async def compact_command(
    messages: list[dict[str, Any]],
    *,
    partial: bool = False,
    preserve_last: int = 6,
) -> dict[str, Any]:
    if partial:
        return await partialCompactConversation(messages, preserve_last=preserve_last)
    return await compactConversation(messages, preserve_last=preserve_last)


call = compact_command
