"""Slash command implementation for listing configured agents."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Awaitable, Callable

from python_src.cli.handlers.agents import agentsHandler

DoneCallback = Callable[[Any], Any | Awaitable[Any]]


def _context_cwd(context: dict[str, Any] | None) -> str:
    if not context:
        return str(Path.cwd())
    app_state = context.get("appState") if isinstance(context.get("appState"), dict) else {}
    return str(context.get("cwd") or app_state.get("cwd") or Path.cwd())


async def _notify(onDone: DoneCallback | None, payload: Any) -> None:
    if onDone is None:
        return
    result = onDone(payload)
    if hasattr(result, "__await__"):
        await result


async def call(
    onDone: DoneCallback | None = None,
    context: dict[str, Any] | None = None,
    args: str | None = None,
    *,
    cwd: str | None = None,
    json_output: bool | None = None,
) -> dict[str, Any] | str:
    """List project and user agent configurations.

    The TypeScript command is a local JSX command. In the Python runtime the
    output is delegated to the already-migrated CLI handler so `/agents` and the
    headless CLI keep the same source of truth.
    """

    raw_args = args or ""
    wants_json = bool(json_output) or "--json" in raw_args.split()
    result = await agentsHandler(cwd or _context_cwd(context), json_output=wants_json)
    output = json.dumps(result, ensure_ascii=False) if isinstance(result, dict) else result
    await _notify(onDone, output)
    return result
