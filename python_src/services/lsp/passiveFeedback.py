"""Passive feedback helpers for LSP diagnostics."""

from __future__ import annotations

from typing import Any, Callable

from .LSPDiagnosticRegistry import registerPendingLSPDiagnostic


async def formatDiagnosticsForAttachment(diagnostics: list[dict[str, Any]]) -> str:
    if not diagnostics:
        return "No LSP diagnostics."
    lines: list[str] = []
    for diag in diagnostics:
        location = f"{diag.get('path', '<unknown>')}:{diag.get('line', 1)}"
        lines.append(f"{location}: {diag.get('severity', 'warning')}: {diag.get('message', '')}")
    return "\n".join(lines)


async def registerLSPNotificationHandlers(handler: Callable[[dict[str, Any]], Any] | None = None) -> dict[str, Any]:
    async def publish(path: str, diagnostic: dict[str, Any] | str) -> dict[str, Any]:
        entry = await registerPendingLSPDiagnostic(path, diagnostic)
        if handler:
            result = handler(entry)
            if hasattr(result, "__await__"):
                await result
        return entry

    return {"publishDiagnostics": publish}
