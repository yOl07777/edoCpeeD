"""Prompt text for TeamDeleteTool."""

from python_src.tools.TeamDeleteTool.constants import TEAM_DELETE_TOOL_NAME


async def getPrompt(*args, **kwargs) -> str:
    return f"Use {TEAM_DELETE_TOOL_NAME} with the exact team_id returned by team_create."


__all__ = ["getPrompt"]
