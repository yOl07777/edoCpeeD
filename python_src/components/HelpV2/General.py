from __future__ import annotations

from typing import Any

from python_src.components.HelpV2._shared import help_payload


async def General(*args: Any, **kwargs: Any) -> Any:
    return help_payload(
        "help_general",
        title="DeepSeek Code",
        sections=[
            {"title": "Terminal", "text": "Use natural language prompts, slash commands, @file mentions, and ! shell shortcuts."},
            {"title": "Files", "text": "Use /write and /append for direct local writes, or let enabled tools edit workspace files."},
            {"title": "Models", "text": "Configure DEEPSEEK_API_KEYS and choose deepseek-chat, deepseek-coder, or compatible endpoints."},
        ],
        cwd=str(kwargs.get("cwd") or ""),
    )


__all__ = ["General"]
