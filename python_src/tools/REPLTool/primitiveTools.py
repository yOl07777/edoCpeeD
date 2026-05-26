"""Primitive tools exposed only in local REPL/test contexts."""

from __future__ import annotations

from typing import Any

from python_src.tools.REPLTool.constants import REPL_ONLY_TOOLS
from python_src.tools.SyntheticOutputTool.SyntheticOutputTool import SyntheticOutputTool
from python_src.tools.testing.TestingPermissionTool import TestingPermissionTool


async def getReplPrimitiveTools(*args: Any, **kwargs: Any) -> list[Any]:
    include = set(kwargs.get("include") or REPL_ONLY_TOOLS)
    tools = []
    if "synthetic_output" in include:
        tools.append(SyntheticOutputTool)
    if "testing_permission" in include:
        tools.append(TestingPermissionTool)
    return tools


__all__ = ["getReplPrimitiveTools"]
