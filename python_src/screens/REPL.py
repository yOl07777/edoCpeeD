"""REPL screen shim for the Python DeepSeek terminal."""

from __future__ import annotations

from typing import Any

from python_src.replLauncher import launchRepl


async def REPL(*args: Any, **kwargs: Any) -> Any:
    """Launch or describe the standalone terminal.

    The original screen is an Ink/React component.  In Python the interactive
    implementation lives in ``deepseek_code.terminal``; this function preserves
    the exported screen boundary and delegates to the launcher.
    """

    dry_run = bool(kwargs.pop("dryRun", kwargs.pop("dry_run", False)))
    argv = kwargs.pop("argv", None)
    if argv is None and args:
        first = args[0]
        if isinstance(first, dict):
            argv = first.get("argv")
            dry_run = bool(first.get("dryRun", first.get("dry_run", dry_run)))
    return await launchRepl(argv=argv or [], dryRun=dry_run, **kwargs)


__all__ = ["REPL"]
