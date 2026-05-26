"""Interactive `/extra-usage` command shim."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


def _load_run_extra_usage():
    path = Path(__file__).with_name("extra-usage-core.py")
    spec = importlib.util.spec_from_file_location("extra_usage_core_interactive", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.runExtraUsage


async def call(onDone: Any = None, context: Any = None, *_args: Any, **_kwargs: Any) -> None:
    runExtraUsage = _load_run_extra_usage()
    result = await runExtraUsage()
    if result["type"] == "message":
        message = str(result["value"])
    else:
        message = (
            f"Manage DeepSeek usage at {result['url']}. "
            "Browser opening is intentionally represented as a message in the Python migration."
        )
    if callable(onDone):
        try:
            onDone(message, {"display": "system"})
        except TypeError:
            onDone(message)
    if isinstance(context, dict):
        context.setdefault("appState", {})["extraUsageLastResult"] = result
    return None
