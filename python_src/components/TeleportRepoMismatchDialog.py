from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, first_options, option


async def TeleportRepoMismatchDialog(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = first_options(args)
    expected = str(option(args, kwargs, "expected", data.get("expectedRepo", "")) or "")
    actual = str(option(args, kwargs, "actual", data.get("actualRepo", "")) or "")
    return component_payload("teleport_repo_mismatch_dialog", expected=expected, actual=actual, mismatch=bool(expected and actual and expected != actual))


__all__ = ["TeleportRepoMismatchDialog"]
