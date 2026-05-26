"""REPL launcher compatibility layer for DeepSeek Code."""

from __future__ import annotations

from typing import Any


async def launchRepl(*_args: Any, **kwargs: Any) -> int | dict[str, Any]:
    """Launch the standalone DeepSeek terminal, or return a dry-run plan."""

    argv = kwargs.get("argv")
    dry_run = bool(kwargs.get("dryRun", False) or kwargs.get("dry_run", False))
    if dry_run:
        return {
            "type": "repl_launch",
            "provider": "deepseek",
            "entrypoint": "deepseek_code.terminal",
            "argv": list(argv or []),
            "dryRun": True,
        }

    from deepseek_code.terminal import amain

    return await amain(list(argv or []))


__all__ = ["launchRepl"]
