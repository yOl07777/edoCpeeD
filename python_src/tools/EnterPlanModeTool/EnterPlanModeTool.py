from __future__ import annotations

from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.plan_store import enter_plan


async def enter_plan_mode(goal: str, steps: list[dict[str, str]] | None = None) -> dict[str, Any]:
    return enter_plan(goal, steps).to_dict()


EnterPlanModeTool = PythonTool(
    name="enter_plan_mode",
    description="Enter plan mode with a goal and optional steps.",
    parameters=object_schema(
        {
            "goal": {"type": "string"},
            "steps": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "step": {"type": "string"},
                        "status": {"type": "string"},
                    },
                    "required": ["step", "status"],
                    "additionalProperties": False,
                },
            },
        },
        required=["goal"],
    ),
    handler=enter_plan_mode,
    read_only=False,
)
