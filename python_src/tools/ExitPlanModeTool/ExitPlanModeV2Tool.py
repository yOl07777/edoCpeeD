from __future__ import annotations

from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.plan_store import exit_plan


async def exit_plan_mode() -> dict[str, Any]:
    return exit_plan().to_dict()


_sdkInputSchema = object_schema({})
outputSchema = {"type": "object"}

ExitPlanModeV2Tool = PythonTool(
    name="exit_plan_mode",
    description="Exit plan mode.",
    parameters=_sdkInputSchema,
    handler=exit_plan_mode,
    read_only=False,
)
