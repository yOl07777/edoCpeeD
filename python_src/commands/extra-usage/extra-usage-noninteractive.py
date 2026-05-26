"""Non-interactive `/extra-usage` command."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


def _load_run_extra_usage():
    path = Path(__file__).with_name("extra-usage-core.py")
    spec = importlib.util.spec_from_file_location("extra_usage_core_noninteractive", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.runExtraUsage


async def call(*_args: Any, **_kwargs: Any) -> dict[str, str]:
    runExtraUsage = _load_run_extra_usage()
    result = await runExtraUsage()
    if result["type"] == "message":
        return {"type": "text", "value": str(result["value"])}
    return {
        "type": "text",
        "value": (
            f"Please visit {result['url']} to manage DeepSeek usage. "
            "This Python migration does not open browsers from non-interactive commands."
        ),
    }
