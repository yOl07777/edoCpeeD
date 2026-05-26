"""Cache cleanup helpers for the Python slash-command runtime."""

from __future__ import annotations

from collections.abc import Callable
from inspect import isawaitable
from typing import Any

CacheClearer = Callable[[], Any]

_CACHE_REGISTRY: dict[str, CacheClearer] = {}


def registerSessionCache(name: str, clear_fn: CacheClearer) -> None:
    """Register a cache clearer owned by a migrated module."""

    if not name:
        raise ValueError("cache name is required")
    _CACHE_REGISTRY[name] = clear_fn


async def _maybe_call(name: str, clear_fn: CacheClearer, cleared: list[str], errors: list[dict[str, str]]) -> None:
    try:
        result = clear_fn()
        if isawaitable(result):
            await result
        cleared.append(name)
    except Exception as exc:  # pragma: no cover - defensive parity with TS cleanup
        errors.append({"name": name, "error": str(exc)})


async def clearSessionCaches(preservedAgentIds: list[str] | None = None) -> dict[str, Any]:
    """Clear lightweight in-process state while preserving external files."""

    cleared: list[str] = []
    errors: list[dict[str, str]] = []

    try:
        from python_src.commands import clearCommandsCache

        await _maybe_call("commands", clearCommandsCache, cleared, errors)
    except Exception as exc:
        errors.append({"name": "commands", "error": str(exc)})

    try:
        from python_src.session_store import SESSION_STATE

        await _maybe_call("session_state", SESSION_STATE.clear, cleared, errors)
    except Exception as exc:
        errors.append({"name": "session_state", "error": str(exc)})

    optional_clearers: list[tuple[str, str, str]] = [
        ("api_dump_prompts", "python_src.services.api.dumpPrompts", "clearAllDumpState"),
        ("prompt_cache_break_detection", "python_src.services.promptCacheBreakDetection", "resetPromptCacheBreakDetection"),
        ("session_ingress", "python_src.services.sessionIngress", "clearAllSessions"),
        ("lsp_diagnostics", "python_src.services.lsp.LSPDiagnosticRegistry", "resetAllLSPDiagnosticState"),
    ]
    for name, module_name, attr in optional_clearers:
        try:
            module = __import__(module_name, fromlist=[attr])
            clear_fn = getattr(module, attr)
        except Exception:
            continue
        await _maybe_call(name, clear_fn, cleared, errors)

    for name, clear_fn in list(_CACHE_REGISTRY.items()):
        await _maybe_call(name, clear_fn, cleared, errors)

    return {
        "cleared": cleared,
        "errors": errors,
        "preservedAgentIds": list(preservedAgentIds or []),
    }
