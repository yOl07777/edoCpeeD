"""Prompt text for TeamCreateTool."""

from python_src.tools.TeamCreateTool.constants import TEAM_CREATE_TOOL_NAME


async def getPrompt(*args, **kwargs) -> str:
    return f"Use {TEAM_CREATE_TOOL_NAME} to create a local in-process team from existing agent ids."


__all__ = ["getPrompt"]
