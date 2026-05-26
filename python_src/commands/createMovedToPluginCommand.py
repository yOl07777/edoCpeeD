"""Helpers for commands that have a plugin-backed public version."""

from __future__ import annotations

import os
from typing import Any, Awaitable, Callable

ContentBlocks = list[dict[str, str]]
PromptFactory = Callable[[str, Any | None], Awaitable[ContentBlocks]]


async def _default_prompt_factory(_args: str, _context: Any | None = None) -> ContentBlocks:
    return [{"type": "text", "text": "This command is available through a DeepSeek Code plugin."}]


def createMovedToPluginCommand(
    *,
    name: str,
    description: str,
    progressMessage: str,
    pluginName: str,
    pluginCommand: str,
    getPromptWhileMarketplaceIsPrivate: PromptFactory | None = None,
) -> dict[str, Any]:
    prompt_factory = getPromptWhileMarketplaceIsPrivate or _default_prompt_factory

    async def getPromptForCommand(args: str = "", context: Any | None = None) -> ContentBlocks:
        if os.getenv("USER_TYPE") == "ant":
            return [
                {
                    "type": "text",
                    "text": (
                        "This command has been moved to a plugin. Tell the user:\n\n"
                        f"1. To install the plugin, run:\n   deepseek plugin install {pluginName}@deepseek-code-marketplace\n\n"
                        f"2. After installation, use /{pluginName}:{pluginCommand} to run this command\n\n"
                        f"3. For more information, see the {pluginName} plugin README.\n\n"
                        "Do not attempt to run the command. Simply inform the user about the plugin installation."
                    ),
                }
            ]
        return await prompt_factory(args or "", context)

    return {
        "type": "prompt",
        "name": name,
        "description": description,
        "progressMessage": progressMessage,
        "contentLength": 0,
        "source": "builtin",
        "userFacingName": lambda: name,
        "getPromptForCommand": getPromptForCommand,
    }
