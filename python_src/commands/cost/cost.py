from __future__ import annotations

from typing import Any

from python_src.cost_store import COST_STATE
from python_src.tools.base import PythonTool, object_schema


async def cost_command(
    action: str = "summary",
    *,
    input_tokens: int = 0,
    output_tokens: int = 0,
    total_usd: float = 0.0,
) -> dict[str, Any]:
    if action == "add":
        COST_STATE.add(input_tokens=input_tokens, output_tokens=output_tokens, total_usd=total_usd)
    elif action == "reset":
        COST_STATE.reset()
    elif action != "summary":
        raise ValueError(f"Unknown cost action: {action}")
    return COST_STATE.to_dict()


call = PythonTool(
    name="cost",
    description="Track or summarize lightweight token/cost usage.",
    parameters=object_schema(
        {
            "action": {"type": "string", "enum": ["summary", "add", "reset"], "default": "summary"},
            "input_tokens": {"type": "integer", "default": 0},
            "output_tokens": {"type": "integer", "default": 0},
            "total_usd": {"type": "number", "default": 0.0},
        },
    ),
    handler=cost_command,
    read_only=False,
)
