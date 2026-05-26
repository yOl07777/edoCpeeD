"""Synthetic output tool shim."""

from __future__ import annotations

import os
from typing import Any

from python_src.tools.base import PythonTool, object_schema

SYNTHETIC_OUTPUT_TOOL_NAME = "synthetic_output"


async def synthetic_output(content: str, *, label: str = "synthetic") -> dict[str, Any]:
    return {"label": label, "content": content, "synthetic": True}


async def isSyntheticOutputToolEnabled(*args: Any, **kwargs: Any) -> bool:
    value = kwargs.get("enabled")
    if value is not None:
        return bool(value)
    return os.getenv("DEEPCODE_SYNTHETIC_OUTPUT", "").lower() in {"1", "true", "yes", "on"}


async def createSyntheticOutputTool(*args: Any, **kwargs: Any) -> PythonTool | None:
    enabled = await isSyntheticOutputToolEnabled(**kwargs)
    if not enabled:
        return None
    return PythonTool(
        name=kwargs.get("name") or SYNTHETIC_OUTPUT_TOOL_NAME,
        description="Return synthetic local output for tests and dry-run workflows.",
        parameters=object_schema(
            {
                "content": {"type": "string"},
                "label": {"type": "string", "default": "synthetic"},
            },
            required=["content"],
        ),
        handler=synthetic_output,
        read_only=True,
    )


SyntheticOutputTool = PythonTool(
    name=SYNTHETIC_OUTPUT_TOOL_NAME,
    description="Return synthetic local output for tests and dry-run workflows.",
    parameters=object_schema(
        {
            "content": {"type": "string"},
            "label": {"type": "string", "default": "synthetic"},
        },
        required=["content"],
    ),
    handler=synthetic_output,
    read_only=True,
)

__all__ = [
    "SYNTHETIC_OUTPUT_TOOL_NAME",
    "SyntheticOutputTool",
    "createSyntheticOutputTool",
    "isSyntheticOutputToolEnabled",
    "synthetic_output",
]
