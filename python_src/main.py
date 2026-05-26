"""Top-level Python entry shim for the migrated DeepSeek runtime."""

from __future__ import annotations

from typing import Any


async def startDeferredPrefetches(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
    """Return local prefetch status; no network prefetch is started."""

    return {
        "type": "deferred_prefetches",
        "provider": "deepseek",
        "started": False,
        "reason": "Python migration shim avoids background network work.",
    }


async def main(*args: Any, **kwargs: Any) -> Any:
    """Delegate to the standalone DeepSeek Code CLI."""

    argv = kwargs.get("argv")
    if argv is None and args:
        first = args[0]
        argv = list(first) if isinstance(first, (list, tuple)) else [str(first)]
    if kwargs.get("dryRun") or kwargs.get("dry_run"):
        return {
            "type": "main_entry",
            "provider": "deepseek",
            "entrypoint": "deepseek_code.cli",
            "argv": list(argv or []),
            "dryRun": True,
        }

    from deepseek_code.cli import amain

    return await amain(list(argv or []))


__all__ = ["main", "startDeferredPrefetches"]
