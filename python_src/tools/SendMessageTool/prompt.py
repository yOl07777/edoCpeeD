"""Prompt text for SendMessageTool."""

from __future__ import annotations

from python_src.tools.SendMessageTool.constants import SEND_MESSAGE_TOOL_NAME

DESCRIPTION = "Send a message to a local in-process agent or team."


async def getPrompt(*args, **kwargs) -> str:
    return f"Use {SEND_MESSAGE_TOOL_NAME} with target_id, content, and optional sender."


__all__ = ["DESCRIPTION", "getPrompt"]
